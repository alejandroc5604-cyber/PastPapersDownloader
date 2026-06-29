import asyncio
import sys

from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner

from utils import *
from downloader import Downloader
import keyboard


class CLI:
    def __init__(self):
        self.DownloaderWorkerNum = 3
        self.SessionsList = []
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
                    content = "\n".join(status_list[-4:]) or "No status"
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
                choose_from = []
                for subject in self.SubjectsList:
                    selection_string = f"{subject.name.ljust(30)} ({subject.code})"
                    choose_from.append(selection_string)
                picker = PickFromList(choose_from, self.layout["left_panel"])
                picker.UpdateTo.update(Panel(picker.UpdateMenu(), title="Select Subject"))
                Entertype, selected_index, selected_option = await picker.Pick()
                if Entertype == "CTRL-ENTER":
                    print("Download All")
                self.selected_subject = self.SubjectsList[selected_index]
                NameandCode = f"{self.selected_subject.name} ({self.selected_subject.code})"
                
                url = self.selected_subject.url
                
                #fetch data from the selected subject
                self.layout["left_panel"].update(
                    Panel(Spinner("bouncingBall", text=f"Fetching data for {NameandCode}", style="green"), title=NameandCode)
                )  
                
                self.SessionsList = await GetSubjectSessionsList(url)
                    
                if not self.SessionsList:
                    self.layout["left_panel"].update(Panel("Nothing Found \n Press any key to continue", title="Error"))
                    keyboard.read_key()
                    continue
                    
                #we now have the sessions from the selected subject
                choose_from = []
                for Session in self.SessionsList:
                    year = Session.Year
                    months = Session.Months
                    selection_string = f"{year} {months}"
                    choose_from.append(selection_string)
                #picking from the sessions of said subject
                picker = PickFromList(choose_from, self.layout["left_panel"])
                picker.UpdateTo.update(Panel(picker.UpdateMenu(), title="Select Session"))
                Entertype, selected_index, selected_option = await picker.Pick()
                self.Selected_Session = self.SessionsList[selected_index]
                
                
                
                
                months = self.Selected_Session.Months
                year = self.Selected_Session.Year
                session_url = self.Selected_Session.Link
                self.layout["left_panel"].update(
                    Panel(Spinner("bouncingBall", text=f"Fetching paper list for {year} {months}...", style="green"), title="Papers")
                )
                
                self.PapersList = await GetSessionPapers(session_url)   
                if Entertype == "CTRL-ENTER":
                    print("Download All Across Session")
                    
                choose_from = []
                for paper in self.PapersList:
                    filename = paper.filename
                    selection_string = str(filename)
                    choose_from.append(selection_string)
                #f"{filename}" for code, week, doctype, paper_num, download_link, filename in self.PapersList
                # list of papers available

                
                picker = PickFromList(choose_from, self.layout["left_panel"])
                picker.UpdateTo.update(Panel(picker.UpdateMenu(), title="Select Paper"))
                if not choose_from:
                    #wait for the user to press any key to continue. lets move them back to the previous screen
                    keyboard.read_key() 
                    
                Entertype, selected_index, selected_option = await picker.Pick()
                selected_paper = self.PapersList[selected_index]
                if Entertype == "CTRL-ENTER":
                    print("Download All Papers")
                else:
                    
                    #code, week, doctype, paper_num, download_link, filename = self.PapersList[selected_index]
                    code = selected_paper.SubjectCode
                    months = selected_paper.Month
                    download_link = selected_paper.DownloadLink
                    formatted_path = Sorter(code, year, months, "IGCSE")
                    await self.downloader.add_url(download_link, formatted_path)
                
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
