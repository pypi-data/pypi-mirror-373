import os

from blueness import module
from bluer_options import string
from bluer_options import host
from bluer_options.logger import crash_report
from bluer_options.timer import Timer
from bluer_objects import file
from bluer_objects import objects
from bluer_objects.storage import upload
from bluer_objects.graphics.signature import add_signature
from bluer_ai import VERSION as abcli_VERSION
from bluer_ai.modules import terraform
from bluer_objects.env import abcli_object_name

from bluer_sbc import NAME
from bluer_sbc import env
from bluer_sbc.host import signature
from bluer_sbc.session.functions import reply_to_bash
from bluer_sbc.algo.diff import Diff
from bluer_sbc.hardware import hardware
from bluer_sbc.imager import imager
from bluer_sbc.logger import logger


NAME = module.name(__file__, NAME)


class Session:
    def __init__(self):
        self.bash_keys = {
            "i": "exit",
            "o": "shutdown",
            "p": "reboot",
            "u": "update",
        }

        self.diff = Diff(env.BLUER_SBC_SESSION_IMAGER_DIFF)

        self.capture_requested = False

        self.frame = 0
        self.new_frame = False
        self.frame_image = terraform.poster(None)
        self.frame_filename = ""

        self.auto_upload = env.BLUER_SBC_SESSION_AUTO_UPLOAD

        self.messages = []

        self.model = None

        self.params = {"iteration": -1}

        self.state = {}

        self.timer = {}
        for name, period in {
            "imager": env.BLUER_SBC_SESSION_IMAGER_PERIOD,
            "messenger": env.BLUER_SBC_SESSION_MESSENGER_PERIOD,
            "reboot": env.BLUER_SBC_SESSION_REBOOT_PERIOD,
            "screen": env.BLUER_SBC_SESSION_SCREEN_PERIOD,
            "temperature": env.BLUER_SBC_SESSION_TEMPERATURE_PERIOD,
        }.items():
            self.add_timer(name, period)

    def add_timer(
        self,
        name: str,
        period: float,
    ):
        if name not in self.timer:
            self.timer[name] = Timer(period, name)
            logger.info(
                "{}: timer[{}]:{}".format(
                    NAME,
                    name,
                    string.pretty_frequency(1 / period),
                )
            )
            return True
        return False

    def check_imager(self):
        self.new_frame = False

        if not env.BLUER_SBC_SESSION_IMAGER_ENABLED:
            return
        if not self.capture_requested and not self.timer["imager"].tick():
            return
        self.capture_requested = False

        if env.BLUER_SBC_CAMERA_KEEP_OPEN:
            if imager.device is None:
                if not imager.open(log=True):
                    return

        success, image = imager.capture(  # pylint: disable=unexpected-keyword-arg
            open_before=not bool(env.BLUER_SBC_CAMERA_KEEP_OPEN),
            close_after=not bool(env.BLUER_SBC_CAMERA_KEEP_OPEN),
        )
        if not success:
            return

        hardware.pulse("data")

        if self.diff.same(image):
            return

        self.frame += 1

        image = add_signature(
            image,
            [" | ".join(objects.signature(self.frame))],
            [" | ".join(signature())],
        )

        filename = objects.path_of(
            object_name=abcli_object_name,
            filename=f"{self.frame:016d}.jpg",
        )
        if not file.save_image(filename, image):
            return

        self.new_frame = True
        self.frame_image = image
        self.frame_filename = filename

        if self.auto_upload:
            upload(
                object_name=abcli_object_name,
                filename=file.name_and_extension(self.frame_filename),
            )

    def check_keys(self):
        for key in hardware.key_buffer:
            if key in self.bash_keys:
                reply_to_bash(self.bash_keys[key])
                return False

        if " " in hardware.key_buffer:
            self.capture_requested = True

        hardware.key_buffer = []

        return None

    def check_seed(self):
        seed_filename = host.get_seed_filename()
        if not file.exists(seed_filename):
            return None

        success, content = file.load_json(file.set_extension(seed_filename, "json"))
        if not success:
            return None

        hardware.pulse("outputs")

        seed_version = content.get("version", "")
        if seed_version <= abcli_VERSION:
            return None

        logger.info(f"{NAME}: seed {seed_version} detected.")
        reply_to_bash("seed", [seed_filename])
        return False

    def check_timers(self):
        if self.timer["screen"].tick():
            hardware.update_screen(
                image=self.frame_image,
                session=self,
                header=self.signature(),
            )
        elif hardware.animated:
            hardware.animate()

        if self.timer["reboot"].tick("wait"):
            reply_to_bash("reboot")
            return False

        if self.timer["temperature"].tick():
            self.read_temperature()

        return None

    def close(self):
        hardware.release()

        if env.BLUER_SBC_CAMERA_KEEP_OPEN:
            imager.close(log=True)

    def process_message(self, message):
        if (
            env.BLUER_SBC_SESSION_OUTBOUND_QUEUE
            and message.subject in "bolt,frame".split(",")
            and not host.is_headless()
        ):
            logger.info(f"{NAME}: frame received: {message.as_string()}")
            self.new_frame, self.frame_image = file.load_image(message.filename)

        if message.subject == "capture":
            logger.info(f"{NAME}: capture message received.")
            self.capture_requested = True

        if message.subject in "reboot,shutdown".split(","):
            logger.info(f"{NAME}: {message.subject} message received.")
            reply_to_bash(message.subject)
            return False

        if message.subject == "update":
            try:
                if message.data["version"] > abcli_VERSION:
                    reply_to_bash("update")
                    return False
            except Exception as e:
                crash_report(e)

        return None

    # https://www.cyberciti.biz/faq/linux-find-out-raspberry-pi-gpu-and-arm-cpu-temperature-command/
    def read_temperature(self):
        if not host.is_rpi():
            return

        params = {}

        success, output = file.load_text("/sys/class/thermal/thermal_zone0/temp")
        if success:
            output = [thing for thing in output if thing]
            if output:
                try:
                    params["temperature.cpu"] = float(output[0]) / 1000
                except Exception as e:
                    crash_report(e)
                    return

        self.params.update(params)
        logger.info(
            "{}: {}".format(
                NAME,
                ", ".join(string.pretty_param(params)),
            )
        )

    def signature(self):
        return [
            " | ".join(objects.signature()),
            " | ".join(sorted([timer.signature() for timer in self.timer.values()])),
            " | ".join(
                (["*"] if self.new_frame else [])
                + (["^"] if self.auto_upload else [])
                + hardware.signature()
                + [
                    "diff: {:.03f} - {}".format(
                        self.diff.last_diff,
                        string.pretty_duration(
                            self.diff.last_same_period,
                            largest=True,
                            include_ms=True,
                            short=True,
                        ),
                    ),
                    string.pretty_shape_of_matrix(self.frame_image),
                ]
                + ([] if self.model is None else self.model.signature())
            ),
        ]

    @staticmethod
    def start():
        success = True
        logger.info(f"{NAME}: started ...")

        try:
            session = Session()

            while session.step():
                pass

            logger.info(f"{NAME}: stopped.")
        except KeyboardInterrupt:
            logger.info(f"{NAME}: Ctrl+C: stopped.")
            reply_to_bash("exit")
        except Exception as e:
            crash_report(e)
            success = False

        try:
            session.close()
        except Exception as e:
            crash_report(e)
            success = False

        return success

    def step(
        self,
        steps="all",
    ) -> bool:
        if steps == "all":
            steps = "imager,keys,messages,seed,switch,timers".split(",")

        self.params["iteration"] += 1

        hardware.pulse("loop", 0)

        for enabled, step_ in zip(
            [
                "keys" in steps,
                "timers" in steps,
                "seed" in steps,
                "imager" in steps,
            ],
            [
                self.check_keys,
                self.check_timers,
                self.check_seed,
                self.check_imager,
            ],
        ):
            if not enabled:
                continue
            output = step_()
            if output in [False, True]:
                return output

            hardware.clock()

        return True
