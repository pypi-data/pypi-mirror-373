from datetime import datetime


class Stopwatch:
    def __init__(self, paused: bool = False):
        """
        Create stopwatch
        :param create_paused: indicates if the stopwatch is paused from the beginning
        """
        self.start_time = None
        self.paused_at = None
        self.total_paused_time = 0
        self.reset(paused)

    def __str__(self):
        """
        Returns run time in seconds
        :return: Returns run time in seconds
        """
        return str(self.get_run_time_in_seconds())

    def pause(self):
        """
        Pause stopwatch
        :return:
        """
        # pokud stopky nejsou pozastavene, tak je pozastavi
        if self.paused_at is None:
            self.paused_at = datetime.now()

    def resume(self):
        """
        Resume paused stopwatch. Nothing will happen ff the stopwatch is not paused.
        :return:
        """
        # pokud stopky nebyly pozastavene, tak nic nedela
        if self.paused_at is None:
            return
        # jinak pricte cas, po ktery byly stopky pausnute a spusti je
        else:
            delta_paused_time = datetime.now() - self.paused_at
            delta_paused_time_seconds = delta_paused_time.seconds + delta_paused_time.microseconds / 1000000
            self.total_paused_time += delta_paused_time_seconds
            self.paused_at = None

    def reset(self, paused: bool = False):
        """
        Reset stopwatch to zero
        :param paused: indicates if the stopwatch is paused from the beginning
        :return:
        """
        self.start_time = datetime.now()
        self.paused_at = None
        self.total_paused_time = 0
        if paused:
            self.paused_at = self.start_time

    def get_run_time_in_seconds(self):
        """
        Returns run time in seconds with decimal points
        :return: Returns run time in seconds with decimal points
        """
        total_paused_time = self.total_paused_time
        now = datetime.now()
        # pokud jsou stopky pozastavene
        if self.paused_at is not None:
            delta_paused_time = now - self.paused_at
            delta_paused_time_seconds = delta_paused_time.seconds + delta_paused_time.microseconds / 1000000
            total_paused_time += delta_paused_time_seconds
        # spocita jak dlouho stopky bezely
        run_time = now - self.start_time
        run_time_seconds = run_time.seconds + run_time.microseconds / 1000000
        run_time_seconds -= total_paused_time
        return round(run_time_seconds, 6)
