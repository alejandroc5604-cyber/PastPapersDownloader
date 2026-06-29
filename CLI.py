import asyncio
import sys

from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from textual.widgets import OptionList

from utils import *
from downloader import Downloader


class CLI:
    def __init__(self):
        self.DownloaderWorkerNum = 3
        self.CurrentYearList = []
        self.console = Console()
        self.layout = Layout()

    async def LoadSubjectListIGCSE(self):
        self.SubjectsList = await GetSubjectListIGCSE()
        self.layout["left_panel"].update(
            Panel(f"Loaded {len(self.SubjectsList)} subjects", title="Subjects")
        )

    async def LoadDownloaders(self):
        self.downloader = Downloader(num_workers=self.DownloaderWorkerNum)
        await self.downloader.start()

    async def DownloadersPage(self):
        while True:
            try:
                panels = []
                for worker_id, worker in enumerate(self.downloader.workers):
                    status_list = await worker.GetStatusList()
                    content = "\n".join(status_list[-10:]) or "No status"
                    panels.append(Panel(content, title=f"Worker {worker_id}"))
                self.layout["right_panel"].update(
                    Panel(Group(*panels), title=f"Downloaders ({self.DownloaderWorkerNum} workers)")
                )
                await asyncio.sleep(0.2)
            except asyncio.CancelledError:
                break
    async def IGCSE_Handler(self):
        await self.LoadDownloaders()
        await self.LoadSubjectListIGCSE()

        self.updater_task = asyncio.create_task(self.DownloadersPage())
        try:
            while True:
                #Picking from the subject list
                choose_from = [f"{str(name).ljust(30)} ({code})" for name, code, url in self.SubjectsList]
                picker = PickFromList(choose_from, self.layout["left_panel"])
                picker.UpdateTo.update(Panel(picker.generate_menu_renderable(), title="Selection Screen"))
                
                Entertype, selected_index, selected_option = await picker.Pick()
                if Entertype == "CTRL-ENTER":
                    print("Download All")
                    
                # 2. Picking from individual year / sessions
                title = f"{selected_option}".replace(" ", "").replace("(", " (")
                url = self.SubjectsList[selected_index][2]
                
                
                self.layout["left_panel"].update(
                    Panel(Spinner("bouncingBall", text=f"Fetching data for {title}", style="green"), title=title)
                )  
                
                self.CurrentYearList = await GetYearExamsFromSubjectURL(url)
                    
                if not self.CurrentYearList:
                    self.layout["left_panel"].update(Panel("Nothing Found", title="Error"))
                    await asyncio.sleep(2)
                    continue
                    
                choose_from = [f"{year} {months}" for name, code, year, months, link in self.CurrentYearList]
                
                #Picking from the sessions of said subject
                picker = PickFromList(choose_from, self.layout["left_panel"])
                picker.UpdateTo.update(Panel(picker.generate_menu_renderable(), title="Select Session"))
                Entertype, selected_index, selected_option = await picker.Pick()
                
                # Cache year/month meta before overwriting or moving down scope
                _, _, selected_year, selected_month, session_url = self.CurrentYearList[selected_index]
                
                self.layout["left_panel"].update(
                    Panel(Spinner("bouncingBall", text="Fetching paper list...", style="green"), title="Papers")
                )
                
                self.month_year_sessionList = await GetYearExamsFromYearMonthURL(session_url)   
                if Entertype == "CTRL-ENTER":
                    print("Download All Across Session")
                    
                choose_from = [f"{filename}" for code, week, doctype, paper_num, download_link, filename in self.month_year_sessionList]
                
                # list of papers available
                picker = PickFromList(choose_from, self.layout["left_panel"])
                picker.UpdateTo.update(Panel(picker.generate_menu_renderable(), title="Select Paper"))
                Entertype, selected_index, selected_option = await picker.Pick()
                
                if Entertype == "CTRL-ENTER":
                    print("Download All Papers")
                else:
                    # Cleaned variable destructuring mapping exactly to tuple index schemas
                    code, week, doctype, paper_num, download_link, filename = self.month_year_sessionList[selected_index]
                    formatted_path = Sorter(int(code), int(selected_year), selected_month, "IGCSE")
                    self.downloader.add_url(download_link, formatted_path)
                    await self.downloader.start()
                
        except KeyboardInterrupt:
            print('User Exit')   
        finally:
            self.updater_task.cancel()
            await asyncio.gather(self.updater_task, return_exceptions=True)
            await self.downloader.stop()
    async def main(self):
        await self.IGCSE_Handler()
        

    async def setup(self):
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main")
        )
        self.layout["main"].split_row(
            Layout(name="left_panel"),
            Layout(name="right_panel")
        )
        self.layout["header"].update(Panel("Past Paper Downloader", style="bold white on blue"))
        self.layout["left_panel"].update(Panel(Spinner("bouncingBall", text="Fetching Subjects...", style="green"), title="Actions"))
        self.layout["right_panel"].update(Panel(Spinner("bouncingBall", text="Loading Downloaders...", style="green"), title="Downloaders"))

        # Maintain a singular global active Live instance here
        with Live(self.layout, console=self.console, refresh_per_second=20):
            await self.main()

        print("Exited Program")
        sys.exit()


async def MainRunner():
    cli = CLI()
    await cli.setup()


if __name__ == "__main__":
    asyncio.run(MainRunner())
