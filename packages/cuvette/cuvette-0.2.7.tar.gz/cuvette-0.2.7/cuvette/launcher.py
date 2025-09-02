import argparse
import curses
import itertools
import os
import queue
import random
import re
import subprocess
import sys
import textwrap
import threading
import time
from typing import Optional

from cuvette.constants import CLUSTERS
from cuvette.figlet import Figlet

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SESSION_NAME = "👋davidh👋"

SESSION_NAME = "eval-debugging"
SESSION_WORKSPACE = "ai2/olmo-3-evals"
SESSION_PRIORITY = "high"

LAUNCH_COMMAND = """\
beaker session create \
    --name {name} \
    {gpu_command} \
    {cluster_command} \
    {hostname_command} \
    --image beaker://davidh/davidh-interactive \
    --workspace {workspace} \
    --priority {priority} \
    --budget ai2/oe-base \
    --bare \
    --detach \
    --port 8000 --port 8001 --port 8080 --port 8888 \
    --workdir /oe-eval-default/davidh \
    --mount src=weka,ref=oe-eval-default,dst=/oe-eval-default \
    --mount src=weka,ref=oe-training-default,dst=/oe-training-default \
    --mount src=weka,ref=oe-data-default,dst=/oe-data-default \
    --mount src=weka,ref=oe-adapt-default,dst=/oe-adapt-default \
    --mount src=secret,ref=davidh-ssh-key,dst=/root/.ssh/id_rsa \
    --mount src=secret,ref=davidh-aws-creds,dst=/root/.aws/credentials \
    --mount src=secret,ref=davidh-gcp-creds,dst=/root/.gcp/service-account.json \
    --mount src=secret,ref=davidh-kaggle-creds,dst=/root/.kaggle/kaggle.json \
    --secret-env AWS_CONFIG=davidh_AWS_CONFIG \
    --secret-env AWS_CREDENTIALS=davidh_AWS_CREDENTIALS \
    --secret-env davidh_COMET_API_KEY=davidh_COMET_API_KEY \
    --secret-env COMET_API_KEY=davidh_COMET_API_KEY \
    --secret-env R2_ACCESS_KEY_ID=davidh_R2_ACCESS_KEY_ID \
    --secret-env R2_SECRET_ACCESS_KEY=davidh_R2_SECRET_ACCESS_KEY \
    --secret-env HF_TOKEN=davidh_HF_TOKEN \
    --secret-env OPENAI_API_KEY=davidh_OPENAI_API_KEY \
    --secret-env ANTHROPIC_API_KEY=davidh_ANTHROPIC_API_KEY \
    --secret-env BEAKER_TOKEN=davidh_BEAKER_TOKEN \
    --secret-env WANDB_API_KEY=davidh_WANDB_API_KEY \
    --secret-env lambda_AWS_ACCESS_KEY_ID=lambda_AWS_ACCESS_KEY_ID \
    --secret-env lambda_AWS_SECRET_ACCESS_KEY=lambda_AWS_SECRET_ACCESS_KEY \
    -- /entrypoint.sh\
"""

UPDATE_PORT_CMD = "bport {session_id}"


# this might be a bit much...
QUOTES = [
    "Science is what we understand well enough to explain to a computer. Art is everything else we do. (Knuth, 1995)",  # https://www2.math.upenn.edu/~wilf/foreword.pdf
    "Science advances whenever an Art becomes a Science. (Knuth, 1995)",
    "If a machine is expected to be infallible, it cannot also be intelligent. (Turing, 1947)",  # https://plato.stanford.edu/entries/turing/
    "I believe that in about fifty years' time it will be possible to programme computers, with a storage capacity of about 10^9, to make them play the imitation game so well that an average interrogator will not have more than 70 per cent chance of making the right identification after five minutes of questioning. (Turing, 1950)",
    "Machines take me by suprise with great frequency. This is largely because I do not do sufficient calculation to decide what to expect them to do, or rather because, although I do a calculation, I do it in a hurried, slipshod fashion, taking risks. (Turing, 1950)",
    "We offer no explanation as to why these architectures seem to work; we attribute their success, as all else, to divine benevolence. (Shazeer, 2020)",
    "OLMo_θ(x)=softmax(H^L W_O), H^L=f^L∘f^{L-1}∘...∘f^1(E), E=W_Ex + W_Pt, Attn(Q,K,V)=softmax( QK^T / √d_k )V, Q=XW_Q, K=XW_K, V=XW_V, H=concat(H_1, ..., H_h)W_O, H^l = LN(H^{l-1} + Attn(Q,K,V)), Z^l = LN(H^l + FFN(H^l)), FFN(x)=max(0, xW_1+b_1)W_2+b_2, L=-∑ylog(ŷ), θ←θ-η∇L",
    "http://www.ai.mit.edu/lab/gsb/gsl-archive/gsl95-12dec08.html (I found this on Lilian Lee's website)",
    "Thus we may have knowledge of the past but cannot control it; we may control the future but have no knowledge of it. (Shannon, 1959)",  # https://www.gwern.net/docs/cs/1959-shannon.pdf
    "What's the relation between how I think and how I think I think? (Minsky, 1979)",
    "My wife still uses Emacs, which is the most contentious point in our marriage. (Weinberger, 2024)",  # https://quotes.cs.cornell.edu
    "Our modest goal is world domination. (Patterson, 2015, describing the RISC-V project)",  # https://quotes.cs.cornell.edu/speaker/Dave-Patterson/
    "A picture is worth a thousand words, a video is worth a thousand pictures and a demo a thousand videos. So we're up to, um, ten to the nine. (LeCun, 2004)",  # https://quotes.cs.cornell.edu/speaker/Yann--LeCun/
    "Although perhaps of no practical importance, the question is of theoretical interest, and it is hoped that a satisfactory solution of this problem will act as a wedge in attacking other problems of a similar nature and of greater significance. (Shannon on Chess, 1950)",  # https://vision.unipv.it/IA1/ProgrammingaComputerforPlayingChess.pdf
    "What is now proved was once only imagined. (William Blake, 1790)",
    "There ain't no such thing as a free lunch",  # https://ieeexplore.ieee.org/document/585893 (Wolpert & Macready, 2002) -- Although AFAIK the quote came before the term was adopted by the field
    "From one gut feeling I derive much consolation: I suspect that machines to be programmed in our native tongues — be it Dutch, English, American, French, German, or Swahili — are as damned difficult to make as they would be to use. (Dijkstra, 1978)",  # https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD667.html
    "Instruction tables will have to be made up by mathematicians with computing experience and perhaps a certain puzzle-solving ability… This process of constructing instruction tables should be very fascinating. There need be no real danger of it ever becoming a drudge, for any processes that are quite mechanical may be turned over to the machine itself. (Turing, 1945)",  # https://people.csail.mit.edu/asolar/SynthesisCourse/Lecture1.htm
    "The fundamental problem of communication is that of reproducing at one point either exactly or approximately a message selected at another point. (Shannon, 1948)",  # https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf
    "An article about computational science in a scientific publication is not the scholarship itself, it is merely advertising of the scholarship. The actual scholarship is the complete software development environment and the complete set of instructions which generated the figures. (Buckheit & Donoho, 1995)",  # https://link.springer.com/chapter/10.1007/978-1-4612-2544-7_5 -- Originally found on https://arxiv.org/pdf/2409.11363#page=2.10
    "Deep Learning waves have lapped at the shores of computational linguistics for several years now, but 2015 seems like the year when the full force of the tsunami hit the major Natural Language Processing (NLP) conferences. However, some pundits are predicting that the final damage will be even worse. (Manning, 2015)",  # https://watermark02.silverchair.com/coli_a_00239.pdf
    "Overall, I think we should feel excited and glad to live in a time when Natural Language Processing is seen as so central to both the further development of machine learning and industry application problems. The future is bright. However, I would encourage everyone to think about problems, architectures, cognitive science, and the details of human language, how it is learned, processed, and how it changes, rather than just chasing state-of-the-art numbers on a benchmark task (Manning, 2015).",  # https://watermark02.silverchair.com/coli_a_00239.pdf
    "I think that the most exciting areas over the next five years will be really understanding text and videos. I will be disappointed if in five years’ time we do not have something that can watch a YouTube video and tell a story about what happened. In a few years time we will put [Deep Learning] on a chip that fits into someone’s ear and have an English-decoding chip that’s just like a real Babel fish. (Hinton, 2014 in a Reddit AMA)",  # https://www.reddit.com/r/MachineLearning/comments/2lmo0l/ama_geoffrey_hinton
    "Intellectually I think that NLP is fascinating, allowing us to focus on highly structured inference problems, on issues that go to the core of ‘what is thought’ but remain eminently practical, and on a technology that surely would make the world a better place (Michael Jordan, 2014)",  # https://watermark02.silverchair.com/coli_a_00239.pdf <- Referenced here
    "DL appears outwardly to be driven entirely by engineering concerns, but its connectionist roots are still strong and, as Pater documents, connectionism was founded on many of the same core principles as modern linguistics. Both fields can achieve more if they work together (Potts, 2018).",  # https://web.stanford.edu/~cgpotts/temp/pater-commentary-by-potts.pdf
]


def send_notification(title, message):
    """Send a notificaiton on MacOS"""
    os.system(f"""osascript -e 'display notification "{message}" with title "{title}"' """)


def get_host_name(session_id):
    command = ["beaker", "session", "describe"]
    if session_id:
        command.append(session_id)

    result = subprocess.run(command, capture_output=True, text=True)

    match = re.search(r"[^\s]*\.reviz\.ai2\.in", result.stdout)

    return match.group(0) if match else None


class ClusterSelector:
    def __init__(self, max_width=80):
        self.clusters = CLUSTERS
        self.current_selection = 0
        self.figlet = Figlet()
        self.max_width = max_width
        fonts = ["rozzo"]
        random.shuffle(fonts)
        self.figlet.setFont(font=fonts[0])
        self.bg_color = curses.COLOR_BLACK
        try:
            import darkdetect  # pip install darkdetect

            self.is_dark_mode = darkdetect.isDark()
        except ImportError:
            self.is_dark_mode = False

    def setup_colors(self):
        # Define colors based on theme
        self.bg_color = curses.COLOR_BLACK if self.is_dark_mode else -1
        if not self.is_dark_mode:
            curses.use_default_colors()

        # Set up color pairs
        curses.init_pair(1, curses.COLOR_GREEN, self.bg_color)  # Regular text
        curses.init_pair(2, curses.COLOR_MAGENTA, self.bg_color)  # Headers/controls
        curses.init_pair(3, curses.COLOR_MAGENTA, self.bg_color)  # Borders
        curses.init_pair(4, curses.COLOR_MAGENTA, self.bg_color)  # Selected item
        curses.init_pair(5, curses.COLOR_MAGENTA, self.bg_color)  # ASCII art

    def draw_ascii_header(self, window):
        max_y, max_x = window.getmaxyx()

        header = self.figlet.renderText("BEAKER")

        # Calculate the width of the ASCII art for centering
        lines = header.split("\n")
        max_width = max(len(line.rstrip()) for line in lines)
        x_offset = (max_x - max_width) // 2

        y = 1
        for line in lines:
            if line.strip():
                try:
                    window.addstr(y, x_offset, line.rstrip(), curses.color_pair(5))
                except curses.error:
                    pass
                y += 1
        return y + 1

    def draw_menu(self, window, start_y: int):
        # Get window dimensions
        max_y, max_x = window.getmaxyx()
        # Use the smaller of max_width or actual terminal width
        display_width = min(self.max_width, max_x)

        # Calculate left offset to center everything
        left_offset = (max_x - display_width) // 2

        # Center the text based on display width
        window.addstr(
            start_y,
            left_offset,
            "Select a Cluster (https://beaker-docs.apps.allenai.org/compute/clusters.html)".center(
                display_width
            ),
            curses.color_pair(2) | curses.A_BOLD,
        )
        window.addstr(start_y + 1, left_offset, "=" * display_width, curses.color_pair(2))

        # Calculate menu dimensions using display width
        menu_width = display_width // 2 - 2

        # Draw the menu box
        for y in range(start_y + 2, max_y - 2):
            window.addstr(y, left_offset, "│" + " " * menu_width + "│", curses.color_pair(3))
        window.addstr(start_y + 2, left_offset, "┌" + "─" * menu_width + "┐", curses.color_pair(3))
        window.addstr(max_y - 2, left_offset, "└" + "─" * menu_width + "┘", curses.color_pair(3))

        # Draw the description box
        desc_x = left_offset + menu_width + 2
        for y in range(start_y + 2, max_y - 2):
            window.addstr(y, desc_x, "│" + " " * menu_width + "│", curses.color_pair(3))
        window.addstr(start_y + 2, desc_x, "┌" + "─" * menu_width + "┐", curses.color_pair(3))
        window.addstr(max_y - 2, desc_x, "└" + "─" * menu_width + "┘", curses.color_pair(3))

        # Draw the clusters
        for idx, (cluster, _, _, _) in enumerate(self.clusters):
            style = (
                curses.color_pair(4) | curses.A_BOLD
                if idx == self.current_selection
                else curses.color_pair(1)
            )
            window.addstr(
                start_y + 3 + idx,
                left_offset + 2,
                f"{'●' if idx == self.current_selection else '○'} {cluster}",
                style,
            )

        # Draw the description
        _, _, description, _ = self.clusters[self.current_selection]
        desc_lines = textwrap.wrap(description, width=menu_width - 4)
        for idx, line in enumerate(desc_lines):
            window.addstr(start_y + 3 + idx, desc_x + 2, line, curses.color_pair(1))

        # Update the controls text to show number key option
        controls = (
            "select [tab] | navigate [up / down] | press [1-8] for GPUs | [q]uit | [t]oggle theme"
        )
        window.addstr(max_y - 1, left_offset, controls.center(display_width), curses.color_pair(2))

    def draw_process_output(
        self, 
        window, 
        cluster_name: Optional[str|list] = None, 
        host_name: Optional[str|list] = None, 
        num_gpus: int = 0
    ):
        gpu_command = ""
        if num_gpus > 0:
            gpu_command = f"--gpus {num_gpus}"  # Use the selected number of GPUs

        cluster_command = ""
        if cluster_name is not None:
            if not isinstance(cluster_name, list):
                cluster_name = [cluster_name]
            for _cluster_name in cluster_name:
                cluster_command += f"--cluster {_cluster_name} "

        hostname_command = ""
        if host_name is not None:
            if not isinstance(host_name, list):
                host_name = [host_name]
            for _host_name in host_name:
                hostname_command += f"--hostname {_host_name} "

        command = LAUNCH_COMMAND.format(
            name=SESSION_NAME,
            workspace=SESSION_WORKSPACE,
            priority=SESSION_PRIORITY,
            gpu_command=gpu_command,
            cluster_command=cluster_command,
            hostname_command=hostname_command,
        )
        command = command.replace("  ", " ")

        max_y, max_x = window.getmaxyx()

        # Clear screen but keep header
        window.clear()
        header_height = self.draw_ascii_header(window)

        # Center the text based on display width
        max_y, max_x = window.getmaxyx()
        display_width = max_x - 5

        # Wrap the quote text
        quote = random.choice(QUOTES)
        wrapped_quote = textwrap.wrap(quote, width=display_width)

        # Display each line of the wrapped quote
        for i, line in enumerate(wrapped_quote):
            window.addstr(header_height + i, 3, line, curses.color_pair(2) | curses.A_ITALIC)
        header_height += len(wrapped_quote)

        # Draw the output box
        box_width = max_x - 6
        box_height = max_y - header_height - 2

        # Draw box borders
        window.addstr(header_height, 2, "┌" + "─" * box_width + "┐", curses.color_pair(3))
        for y in range(header_height + 1, header_height + box_height):
            window.addstr(y, 2, "│" + " " * box_width + "│", curses.color_pair(3))
        window.addstr(
            header_height + box_height, 2, "└" + "─" * box_width + "┘", curses.color_pair(3)
        )

        # Draw quick start command
        gpu_flag = f" -g {num_gpus}" if num_gpus > 0 else ""
        cluster_flag = f" -c {' '.join(cluster_name)}" if cluster_name is not None else ""
        host_flag = f" -H {' '.join(host_name)}" if host_name is not None else ""
        quick_start = f"bl{cluster_flag}{host_flag}{gpu_flag}"
        window.addstr(
            header_height + 1,
            4,
            f"Quick start command: {quick_start}",
            curses.color_pair(2) | curses.A_BOLD,
        )

        # Draw title (moved down by 5 lines to add more spacing)
        try:
            tailscale_output = subprocess.check_output(
                ["tailscale", "status"], stderr=subprocess.STDOUT, text=True
            )
            if "failed to connect to local Tailscale service" in tailscale_output:
                raise subprocess.CalledProcessError(1, "tailscale status")
        except subprocess.CalledProcessError:
            window.addstr(
                header_height + 2,
                4,
                "Error: Tailscale service is not running!",
                curses.color_pair(1),
            )
            window.addstr(max_y - 1, 2, "Press any key to continue...", curses.color_pair(2))
            window.refresh()
            window.getch()
            return False

        output_queue = queue.Queue()
        spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        last_spin_time = time.time()

        process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
        )

        def enqueue_output(out, queue):
            for line in iter(out.readline, ""):
                queue.put(line)
            out.close()

        # Start threads to read stdout and stderr
        threading.Thread(
            target=enqueue_output, args=(process.stdout, output_queue), daemon=True
        ).start()
        threading.Thread(
            target=enqueue_output, args=(process.stderr, output_queue), daemon=True
        ).start()

        # Display output
        lines = []
        max_lines = box_height - 4  # Leave room for header and borders

        window.nodelay(1)  # Make getch non-blocking

        while process.poll() is None or not output_queue.empty():
            try:
                line = output_queue.get_nowait()
                lines.append(line.strip())
                if len(lines) > max_lines:
                    lines.pop(0)

                # Only update the new line instead of clearing everything
                current_line_count = len(lines)
                display_line = lines[-1]
                try:
                    self.add_colored_str(
                        window,
                        header_height + 2 + min(current_line_count - 1, max_lines - 1),
                        4,
                        display_line[: box_width - 6],
                        curses.color_pair(1),
                    )
                except curses.error:
                    pass

                # Update spinner every 100ms while process is still running
                current_time = time.time()
                if current_time - last_spin_time > 0.1:
                    try:
                        if process.poll() is None:  # Only show spinner if process is still running
                            window.addstr(
                                max_y - 3,
                                4,
                                f"{next(spinner)} Launching session...",
                                curses.color_pair(2),
                            )
                        else:
                            window.addstr(max_y - 3, 4, "✓ Session launched!", curses.color_pair(2))
                        last_spin_time = current_time
                    except curses.error:
                        pass

                window.refresh()
            except queue.Empty:
                # Update spinner even when there's no output
                current_time = time.time()
                if current_time - last_spin_time > 0.1:
                    try:
                        window.addstr(
                            max_y - 3,
                            4,
                            f"{next(spinner)} Launching session...",
                            curses.color_pair(2),
                        )
                        last_spin_time = current_time
                    except curses.error:
                        pass
                    window.refresh()
                time.sleep(0.01)  # Prevent CPU spinning

            # Check for 'q' key press to allow canceling
            try:
                if window.getch() == ord("q"):
                    process.terminate()
                    return None
            except curses.error:
                pass

        window.nodelay(0)  # Reset to blocking mode

        # Wait for user to press any key before returning
        window.addstr(max_y - 3, 4, "✓ Session launched!    ", curses.color_pair(2))

        # Extract session ID from the output
        session_id = None
        for line in lines:
            if "Starting session" in line:
                session_id = line.split()[2]  # Gets the session ID from "Starting session {id} ..."
                break

        if session_id:
            try:
                # Get the hostname for printing
                host_name = get_host_name(session_id)

                # Wait 1 second before connecting (or else the locking mechanism fails)
                time.sleep(2)

                # Run the port update script using the same subprocess pattern
                port_process = subprocess.Popen(
                    UPDATE_PORT_CMD.format(session_id=session_id),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1,
                    shell=True,
                    executable="/bin/zsh",
                )

                # Use the same output handling logic
                port_output_queue = queue.Queue()
                threading.Thread(
                    target=enqueue_output,
                    args=(port_process.stdout, port_output_queue),
                    daemon=True,
                ).start()
                threading.Thread(
                    target=enqueue_output,
                    args=(port_process.stderr, port_output_queue),
                    daemon=True,
                ).start()

                # Continue with existing lines instead of starting fresh
                port_lines = lines  # Use the existing lines from the previous process
                max_port_lines = box_height - 4
                spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
                last_spin_time = time.time()

                window.nodelay(1)  # Make getch non-blocking

                while port_process.poll() is None or not port_output_queue.empty():
                    try:
                        line = port_output_queue.get_nowait()
                        port_lines.append(line.strip())
                        if len(port_lines) > max_port_lines:
                            port_lines.pop(0)

                        # Display all visible lines
                        for idx, display_line in enumerate(port_lines[-max_port_lines:]):
                            try:
                                # Clear the line first by writing spaces
                                window.addstr(
                                    header_height + 3 + idx,
                                    4,
                                    " " * (box_width - 6),
                                    curses.color_pair(1),
                                )
                                # Then write the new text
                                self.add_colored_str(
                                    window,
                                    header_height + 3 + idx,
                                    4,
                                    display_line[: box_width - 6],
                                    curses.color_pair(1),
                                )
                            except curses.error:
                                pass

                        # Update spinner
                        current_time = time.time()
                        if current_time - last_spin_time > 0.1:
                            try:
                                if port_process.poll() is None:
                                    window.addstr(
                                        max_y - 3,
                                        4,
                                        f"{next(spinner)} Updating ports...",
                                        curses.color_pair(2),
                                    )
                                last_spin_time = current_time
                            except curses.error:
                                pass

                        window.refresh()
                    except queue.Empty:
                        # Update spinner even when there's no output
                        current_time = time.time()
                        if current_time - last_spin_time > 0.1:
                            try:
                                window.addstr(
                                    max_y - 3,
                                    4,
                                    f"{next(spinner)} Updating ports...",
                                    curses.color_pair(2),
                                )
                                last_spin_time = current_time
                            except curses.error:
                                pass
                            window.refresh()
                        time.sleep(0.01)

                    # Check for 'q' key press to allow canceling
                    try:
                        if window.getch() == ord("q"):
                            port_process.terminate()
                            return None
                    except curses.error:
                        pass

                window.nodelay(0)  # Reset to blocking mode

                if port_process.returncode == 0:
                    updated_notif = f"Session launched with {num_gpus} GPUs on {host_name}"
                    window.addstr(max_y - 3, 4, f"✓ {updated_notif}", curses.color_pair(2))
                    send_notification("Beaker Launch", updated_notif)
                else:
                    error_notif = f"Port update failed ({session_id})"
                    window.addstr(max_y - 3, 4, f"! {error_notif}", curses.color_pair(1))
                    send_notification("Beaker Launch", error_notif)
            except Exception as e:
                error_notif = f"Port update error: {str(e)}"
                window.addstr(max_y - 3, 4, f"! {error_notif}", curses.color_pair(1))
                send_notification("Beaker Launch", error_notif)

        # Store all output lines for later display
        self.final_output_lines = lines

        window.addstr(max_y - 1, 2, "Press any key to continue...", curses.color_pair(2))
        window.refresh()
        window.getch()

        return process.returncode == 0

    def setup(self, stdscr):
        # Setup colors
        curses.start_color()
        self.setup_colors()

        # Set background color based on theme
        if not self.is_dark_mode:
            stdscr.bkgd(" ", curses.color_pair(1))

        # Hide the cursor
        curses.curs_set(0)

    def run_direct(self, stdscr, cluster_name, host_name, num_gpus):
        self.setup(stdscr)
        self.draw_process_output(stdscr, cluster_name, host_name, num_gpus)

    def run(self, stdscr):
        self.setup(stdscr)

        while True:
            stdscr.clear()

            # Draw the interface
            header_height = self.draw_ascii_header(stdscr)
            self.draw_menu(stdscr, header_height)

            # Refresh the screen
            stdscr.refresh()

            # Handle input
            key = stdscr.getch()
            if key == ord("q"):
                break
            elif key == ord("t"):
                self.is_dark_mode = not self.is_dark_mode
                self.setup_colors()
            elif key == curses.KEY_UP and self.current_selection > 0:
                self.current_selection -= 1
            elif key == curses.KEY_DOWN and self.current_selection < len(self.clusters) - 1:
                self.current_selection += 1
            # Add number key handling
            elif key in [ord(str(i)) for i in range(1, 9)]:  # Handle keys 1-8
                num_gpus = int(chr(key))
                _, cluster_name, _, _ = self.clusters[self.current_selection]
                success = self.draw_process_output(stdscr, cluster_name, None, num_gpus)
                if success:
                    return self.clusters[self.current_selection][0]
                else:
                    continue
            # Add enter key handling with defaults
            elif key in [ord("\n"), ord(" ")]:
                _, cluster_name, _, default_n_gpus = self.clusters[self.current_selection]
                # Default to 1 GPU for GPU clusters, 0 for CPU clusters
                num_gpus = default_n_gpus
                success = self.draw_process_output(stdscr, cluster_name, None, num_gpus)
                if success:
                    return self.clusters[self.current_selection][0]
                else:
                    continue

    def parse_ansi_color(self, text):
        # ANSI color code mapping to curses colors
        ansi_to_curses = {
            "30": self.bg_color,
            "31": curses.COLOR_RED,
            "32": curses.COLOR_GREEN,
            "33": curses.COLOR_YELLOW,
            "34": curses.COLOR_BLUE,
            "35": curses.COLOR_MAGENTA,
            "36": curses.COLOR_CYAN,
            "37": curses.COLOR_WHITE,
        }

        parts = []
        current_pos = 0
        current_color = None

        while True:
            # Find next color code
            esc_pos = text.find("\033[", current_pos)
            if esc_pos == -1:
                # Add remaining text with current color
                if current_pos < len(text):
                    parts.append((text[current_pos:], current_color))
                break

            # Add text before escape code
            if esc_pos > current_pos:
                parts.append((text[current_pos:esc_pos], current_color))

            # Find end of escape code
            m_pos = text.find("m", esc_pos)
            if m_pos == -1:
                break

            # Parse color code
            color_code = text[esc_pos + 2 : m_pos]
            if color_code == "00":
                current_color = None
            else:
                current_color = ansi_to_curses.get(color_code)

            current_pos = m_pos + 1

        return parts

    def add_colored_str(self, window, y, x, text, default_color):
        current_x = x
        for text_part, color in self.parse_ansi_color(text):
            try:
                if color is not None:
                    # Create a new color pair for this color if needed
                    pair_num = color + 10  # Offset to avoid conflicts with existing pairs
                    curses.init_pair(pair_num, color, self.bg_color)
                    window.addstr(y, current_x, text_part, curses.color_pair(pair_num))
                else:
                    window.addstr(y, current_x, text_part, default_color)
                current_x += len(text_part)
            except curses.error:
                pass


def main():
    try:
        parser = argparse.ArgumentParser(description="Beaker Launch Tool")
        parser.add_argument("-c", "--clusters", nargs="+", help="Cluster names")
        parser.add_argument("-H", "--hosts", nargs="+", help="Host names")
        parser.add_argument("-g", "--gpus", type=int, help="Number of GPUs")
        args = parser.parse_args()

        selector = ClusterSelector(max_width=100)

        if args.clusters or args.hosts:
            # Direct launch with command line arguments
            success = curses.wrapper(
                selector.run_direct,
                args.clusters,
                args.hosts,
                args.gpus or 0,  # Default to no GPUs if not specified
            )
            if success and hasattr(selector, "final_output_lines"):
                for line in selector.final_output_lines:
                    print(line)
        else:
            # Interactive menu mode
            selected_cluster = curses.wrapper(selector.run)
            if selected_cluster and hasattr(selector, "final_output_lines"):
                for line in selector.final_output_lines:
                    print(line)
    except (KeyboardInterrupt, curses.error):
        sys.exit(0)  # Exit cleanly on Ctrl+C


if __name__ == "__main__":
    main()
