import logging
import os
import sys
from tkinter import Menu

import rumps

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.get_free_gpus import get_free_gpus
from scripts.get_jobs import get_job_data

logging.basicConfig(
    filename="/tmp/widget.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.debug("Starting application")

OPEN_BL_COMMAND = """
osascript -e 'tell application "Terminal"
    set newWindow to do script "bl"
    set bounds of front window to {100, 100, 900, 600} -- {left, top, right, bottom}
end tell'
"""

OPEN_CHROME_COMMAND = 'open -a "Google Chrome" https://beaker.allen.ai/'
OPEN_CLUSTER_COMMAND = (
    'open -a "Google Chrome" https://beaker.allen.ai/orgs/ai2/clusters/{cluster_name}'
)


class GPUMonitorApp(rumps.App):
    def __init__(self):
        super(GPUMonitorApp, self).__init__("...")
        self.menu = []
        # Update every 5 minutes (300 seconds)
        self.timer = rumps.Timer(self.update_gpu_info, 300)
        self.timer.start()
        self.username = "davidh"
        self.workspace = "davidh"
        logging.debug("App initialized")

    @rumps.clicked("Refresh")
    def refresh(self, _):
        self.title = "..."
        self.update_gpu_info(None)

    @rumps.clicked("beaker.allen.ai")
    def open_beaker(self, _):
        os.system(OPEN_CHROME_COMMAND)

    def open_bl(self, _):
        os.system(OPEN_BL_COMMAND)

    def open_cluster(self, menu_item):
        cluster_name = menu_item.title.split("ai2/")[
            1
        ]  # "4 GPUs: ai2/titan-cirrascale" => "titan-cirrascale"
        os.system(OPEN_CLUSTER_COMMAND.format(cluster_name=cluster_name))

    def dummy(self, _):
        return ""

    def open_workload(self, sender):
        # Extract workload ID from sender's represented_object
        id, workload = sender.represented_object
        if workload:
            url = f"https://beaker.allen.ai/orgs/ai2/workspaces/{self.workspace}/work/{workload}?jobId={id}"
            os.system(f'open -a "Google Chrome" "{url}"')

    def update_gpu_info(self, _):
        try:
            free_gpus = get_free_gpus()

            print(free_gpus)

            # Update the title with a summary
            total_gpus = sum(free_gpus.values())

            title = f"{total_gpus} GPUs"
            self.title = title

            # Create new menu
            self.menu: Menu
            self.menu.clear()
            self.menu = [
                rumps.MenuItem("♻️ Refresh", callback=self.refresh),
                rumps.MenuItem("🚀 beaker.allen.ai", callback=self.open_beaker),
                None,  # This creates a separator in rumps
            ]

            self.menu.add(rumps.MenuItem("Clusters"))
            for k, v in sorted(free_gpus.items(), key=lambda x: x[1], reverse=True):
                menu_item = rumps.MenuItem(
                    f"{v} GPUs: {k}", callback=self.open_cluster
                )  # self.open_bl
                self.menu.add(menu_item)

            processed_jobs = get_job_data(username=self.username, sessions_only=True)

            if len(processed_jobs) == 0:
                # If there's no running jobs, end here
                return

            # Add sep
            self.menu.add(None)

            self.menu.add(rumps.MenuItem(f"Sessions for {self.username}"))

            total_used_gpus = 0
            for job in processed_jobs:
                hostname = job["hostname"]
                gpus = job["gpus"]
                kind = job["kind"]
                name = job["name"]
                workload = job["workload"]
                id = job["id"]

                total_used_gpus += int(gpus)

                if job["is_canceling"]:
                    continue  # just skip these
                elif job["start_date"] is None:
                    job_info = f"[Queued] {kind}: {name}"
                else:
                    gpu_label = f"{gpus} GPUs" if int(gpus) > 0 else "CPU"
                    job_info = f"{gpu_label} {kind}: {name} on {hostname}"  # for ongoing jobs

                if len(job_info) > 40:
                    job_info = job_info[: 40 - 3] + "..."

                menu_item = rumps.MenuItem(
                    job_info, callback=self.dummy if workload is None else self.open_workload
                )
                menu_item.represented_object = (id, workload)  # Store the workload ID
                self.menu.add(menu_item)

            if total_used_gpus > 0:
                title += f" ({total_used_gpus})"
            self.title = str(title)

        except Exception as e:
            logging.error(f"Error: {str(e)}", exc_info=True)
            self.title = "ERR"
            self.menu.add(rumps.MenuItem(f"Error: {str(e)}"))


def main():
    if sys.version_info >= (3, 11):
        raise RuntimeError("Widget requires Python <= 3.10 or lower due to rumps / _tkinter compatibility")

    try:
        GPUMonitorApp().run()
    except Exception as e:
        logging.error(f"Error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()