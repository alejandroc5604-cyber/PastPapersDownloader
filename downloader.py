import os
import aiohttp
import asyncio
import utils

class Downloader():
    def __init__(self, starting_links=None, num_workers=4):
        self.queue = asyncio.Queue()
        self.workers = []
        self.WorkerTasks = []
        self.num_workers = num_workers
        if starting_links:
            for item in starting_links:
                self.queue.put_nowait(item)

    async def GetWorkerData(self, ListIndex):
        return self.workers[ListIndex]
    async def start(self):
        for id in range(self.num_workers):
            self.workers.append(Worker(self.queue, id))
        for worker in self.workers:
            self.WorkerTasks.append(asyncio.create_task(worker.InitializeWorker()))

    async def stop(self):
        await self.queue.join()
        for _ in range(self.num_workers):
            await self.queue.put(("STOP", "STOP"))

        await asyncio.gather(*self.WorkerTasks)

    async def add_url(self, url, path):
        await self.queue.put((url, path))


class Worker:
    def __init__(self, Queue: asyncio.Queue, worker_id=None):
        self.queue = Queue
        self.StatusListLock = asyncio.Lock()
        self.StatusList = []
        self.worker_id = worker_id
        self.FileSize = 0
        self.AmountDownloaded = 0
        self.CurrentFile = ""
        self.PID = os.getpid()

    async def UpdateStatusList(self, message):
        async with self.StatusListLock:
            self.StatusList.append(message)

    async def GetStatusList(self):
        async with self.StatusListLock:
            return self.StatusList.copy()

    def _write_file(self, filepath, data_chunks):
        with open(filepath, "wb") as f:
            for chunk in data_chunks:
                f.write(chunk)

    async def InitializeWorker(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            await self.UpdateStatusList("Worker Initialized")
            while True:
                url, savepath = await self.queue.get()
                
                if url == "STOP":
                    await self.UpdateStatusList("Worker Stopped")
                    self.queue.task_done()
                    break
                await self.UpdateStatusList(f"Gotten {os.path.basename(url)}")
                os.makedirs(savepath, exist_ok=True)
                filename = os.path.basename(url)
                try:
                    await self.UpdateStatusList(f"Downloading {filename}")
                    async with session.get(url) as response:
                        if response.status != 200:
                            await self.UpdateStatusList(f"Failed: HTTP {response.status}")
                            continue  
                        filepath = os.path.join(savepath, filename)
                        self.CurrentFile = filename
                        self.FileSize = int(response.headers.get("content-length", 0))
                        self.AmountDownloaded = 0
                        
                        chunks = []
                        async_iterator = response.content.iter_chunked(8192)
                        async for chunk in async_iterator:
                            chunks.append(chunk)
                            self.AmountDownloaded += len(chunk)

                        await asyncio.to_thread(self._write_file, filepath, chunks)
                        
                        await self.UpdateStatusList(f"Finished {filename}. Worker available")
                except Exception as e:
                    await self.UpdateStatusList(f"Error: {e}")
                finally:
                    self.queue.task_done()


async def main():
    #
    url = r"https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload/0620_w25_qp_12.pdf"

    downloader = Downloader()
    await downloader.start()
    
    await downloader.add_url(url, utils.Sorter("0620", "2025", "w", "IGCSE"))
    await downloader.queue.join()
    await downloader.stop()



if __name__ == "__main__":
    asyncio.run(main())