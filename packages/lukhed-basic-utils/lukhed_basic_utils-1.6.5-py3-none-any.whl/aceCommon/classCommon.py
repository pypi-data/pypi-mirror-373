from aceCommon import osCommon as osC
from aceCommon import fileCommon as fC
from aceCommon import timeCommon as tC

class AceLogging:
    """
    Provides basic logging functionality for classes, writing logs to a JSON file.

    Logs are structured hierarchically by date, with each run assigned a unique ID.
    By default, logs are stored in the directory `logs/projectLogs.json`.

    Attributes:
        ace_logging (bool): Whether logging is enabled.
        ace_log_directory (str): The directory where the log file will be stored.
        ace_log_file_path (str): Full path to the log file.
        ace_log_time_stamp (str): Timestamp for the current date in "%Y%m%d" format.
        log_run_id (int): ID for the current run.

    Methods:
        logging_add_event: Adds an event log to the current run.
        logging_print_active_log: Prints all events logged during the current run.
        print_log_items_by_specified_tag: Filters and prints logs by a specified tag (e.g., "ERROR").

    Example Usage:
        An example of logging in a custom class:
        
        ```python
        class MyCustomClass(AceLogging):
            def __init__(self, logging=True):
                AceLogging.__init__(self, logging=logging)

            def example_custom_method(self):
                test = "do some stuff"
                # some error occurs you want to log
                self.logging_add_event(log_type_named="error", function_named="example_custom_method", 
                                       short_description="A test to check logging functionality"
                                       any_content={"someData": "you want to save"})
        ```
    """
    def __init__(self, log_directory=None, logging=False, custom_file_name=None):
        self.ace_logging = logging
        if self.ace_logging:
            if custom_file_name is None:
                self.ace_logging_fn = "projectLogs.json"
            else:
                self.ace_logging_fn = custom_file_name

            if log_directory is None:
                self.ace_log_directory = osC.create_file_path_string(["logs"])
            else:
                self.ace_log_directory = log_directory

            self.ace_log_file_path = osC.append_to_dir(self.ace_log_directory, self.ace_logging_fn)
            self.ace_log_time_stamp = tC.get_today_date(convert_to_string_format="%Y%m%d")
            self._check_create_dir_structure()

    def _check_create_dir_structure(self):
        if not osC.check_if_dir_exists(self.ace_log_directory):
            osC.create_dir(self.ace_log_directory)
        if not osC.check_if_file_exists(self.ace_log_file_path):
            self.ace_active_log = {self.ace_log_time_stamp: {"totalRuns": 1, "eventsLogged": []}}
            fC.dump_json_to_file(self.ace_log_file_path, self.ace_active_log)
            self.log_run_id = 1
        else:
            self.ace_active_log = fC.load_json_from_file(self.ace_log_file_path)
            try:
                tr = self.ace_active_log[self.ace_log_time_stamp]["totalRuns"]
                tr = tr + 1
                self.log_run_id = tr
                self.ace_active_log[self.ace_log_time_stamp]["totalRuns"] = tr
                self._write_to_log()
            except KeyError:
                self.ace_active_log.update({self.ace_log_time_stamp: {}})
                self.ace_active_log[self.ace_log_time_stamp] = {"totalRuns": 1, "eventsLogged": []}
                self.log_run_id = 1
                self._write_to_log()

    def _write_to_log(self):
        fC.dump_json_to_file(self.ace_log_file_path, self.ace_active_log)


    def logging_add_event(self, log_type_named=None, function_named=None, short_description=None,
                          any_content=None):
        """
        Adds an event to the log file for the current run.

        Parameters:
            log_type_named (str, optional): The type of log (e.g., "ERROR", "INFO").
            function_named (str, optional): The name of the function generating the log.
            short_description (str, optional): A brief description of the event.
            any_content (dict, optional): Additional details related to the event.

        Returns:
            None
        """

        if self.ace_logging:
            if log_type_named is None:
                pass
            else:
                log_type_named = log_type_named.upper()

            log_event = {
                "runNumber": self.log_run_id,
                "timeLogged": tC.create_timestamp(output_format="%Y%m%d%H%M%S"),
                "logType": log_type_named,
                "functionName": function_named,
                "description": short_description,
                "details": any_content
            }

            self.ace_active_log[self.ace_log_time_stamp]["eventsLogged"].append(log_event)
            self._write_to_log()

    def logging_print_active_log(self):
        print("\n****** All Log Events for Current Run ******")
        current_log = [x for x in self.ace_active_log[self.ace_log_time_stamp]["eventsLogged"]
                       if x["runNumber"] == self.log_run_id]
        count = 1
        for log in current_log:
            print("\nEvent = " + str(count))
            print(log['logType'] + "," + log['timeLogged'] + "," + log["functionName"])
            print(log["description"])
            print(log["details"])
            count = count + 1


    def print_log_items_by_specified_tag(self, tag="ERROR", printing=True, last_run_only=True, spec_date=None,
                                         date_format="%Y%m%d", headless_mode=False):
        """
        Prints or retrieves logs filtered by a specific tag (e.g., "ERROR").

        Parameters:
            tag (str): The tag to filter logs (default is "ERROR").
            printing (bool): If True, logs will be printed; otherwise, results are returned.
            last_run_only (bool): If True, filters logs from the most recent run only.
            spec_date (str, optional): Specific date to filter logs (format specified by `date_format`).
            date_format (str): Format of the provided date (default is "%Y%m%d").
            headless_mode (bool): If True, disables interactive prompts and returns results as a list.

        Returns:
            list: Filtered logs matching the specified criteria.
        """

        log = fC.load_json_from_file(self.ace_log_file_path)

        if last_run_only:
            last_date = {}
            for key in log:
                last_date = log[key]

            total_runs = last_date["totalRuns"]
            specified_logs = [x for x in last_date["eventsLogged"] if x["runNumber"] == total_runs]
        elif spec_date is not None:
            date_key = tC.convert_date_format(spec_date, from_format=date_format, to_format="%Y%m%d")
            specified_logs = log[date_key]["eventsLogged"]
        else:
            specified_logs = []
            for key in log:
                specified_logs.extend(log[key]["eventsLogged"])

        found_logs = [x for x in specified_logs if x["logType"].lower() == tag.lower()]


        if printing:
            for temp_log in found_logs:
                print("Time= " + temp_log["timeLogged"])
                print("Function Name= " + temp_log["functionName"])
                print("Description= " + temp_log["description"])
                print("\n")

            if headless_mode is False:
                input("Press any key to close")

        return found_logs


class AceJobScheduler(AceLogging):
    """
    Extends `AceLogging` to include job scheduling functionality.

    This class tracks and manages job execution based on various scheduling requirements 
    (e.g., daily, weekly, after a certain time).

    Attributes:
        ace_job_scheduler_date (str): Current date in "%Y%m%d" format.
        ace_job_scheduler_fn (str): Name of the job status file.

    Methods:
        _check_if_job_needs_running: Determines whether a job should run based on the provided schedule.
        _write_job_status: Updates the job status file after execution.
    """
    def __init__(self, log_setting=True, job_status_file_name="jobStatus.json"):
        AceLogging.__init__(self, logging=log_setting)
        self.ace_job_scheduler_date = tC.get_today_date(convert_to_string_format="%Y%m%d")
        self.ace_job_scheduler_fn = job_status_file_name

    def _create_new_job_status_file_for_job(self, job_dir):
        job_status = {
            "lastRunDate": None,
            "lastRunDay": None,
            "lastRunHour": None,
            "lastRunMinute": None,
            "lastRunSecond": None,
            "lastRunSuccess": None,
            "lastRunMonth": None,
            "lastRunDayName": None,
            "lastRunTimeStamp": None
        }

        new_file = osC.append_to_dir(job_dir, self.ace_job_scheduler_fn)
        fC.dump_json_to_file(new_file, job_status)
        self.logging_add_event("info", "_create_job_status_file_for_job", "created new job status file",
                               {"file": new_file})

    def _get_job_status_json(self, job_dir):
        osC.check_create_dir_structure(job_dir, full_path=True)
        job_status_file = osC.append_to_dir(job_dir, self.ace_job_scheduler_fn)
        if not osC.check_if_file_exists(job_status_file):
            self._create_new_job_status_file_for_job(job_dir)
        return fC.load_json_from_file(job_status_file)

    def _check_if_job_needs_running(self, job_dir, requirement="daily", after_hour=0):
        """
        Determines whether a job should run based on the given requirement.

        Parameters:
            job_dir (str): Directory for the job status file.
            requirement (str): Scheduling requirement, options include:
                - "daily": Runs once per day.
                - "hourly": Runs once per hour.
                - "weekly": Runs once per week.
                - A specific day (e.g., "monday").
                - A list of days (e.g., ["monday", "wednesday"]).
                - "X min": Runs if more than X minutes have passed since the last run.
            after_hour (int): The earliest hour (in 24-hour format) at which the job can run.

        Returns:
            bool: True if the job should run, False otherwise.
        """

        requirement = requirement.lower()
        job_status = self._get_job_status_json(job_dir)
        cur_ts = tC.create_timestamp(output_format="%Y%m%d%H%M%S")
        time_components = tC.extract_date_time_components(cur_ts, input_format="%Y%m%d%H%M%S")
        {'year': 2024, 'month': 12, 'day': 22, 'hour': 15, 'minute': 30, 'second': 45}
        month = time_components['month']
        day = time_components['day']
        hour = time_components['hour']
        minute = time_components['minute']
        second = time_components['second']

        # Must be greater than or equal to after hour to need a run. Need to check this first.
        if hour < after_hour:
            self.logging_add_event("info", "_check_if_job_needs_running",
                                   "determined job does not need to run: after hour requirement", {"job": job_dir})
            return False

        # check daily related requirements
        days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if type(requirement) is list:
            temp_flag = False
            today = tC.get_current_day().lower()
            for req in requirement:
                if req in days_of_week:
                    if today != requirement:
                        pass
                    else:
                        temp_flag = True

            if temp_flag:
                pass
            else:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job does not need to run: daily requirement",
                                       {"job": job_dir})
                return False
        else:
            if requirement in days_of_week:
                today = tC.get_current_day().lower()
                if today != requirement:
                    self.logging_add_event("info", "_check_if_job_needs_running",
                                           "determined job does not need to run: daily requirement",
                                           {"job": job_dir})
                    return False


        # If got here, then day and hour is satisfied. So if last run is None, need to run.
        success = job_status["lastRunSuccess"]
        if job_status["lastRunDate"] is None:
            self.logging_add_event("info", "_check_if_job_needs_running",
                                   "determined job needs to run: no job status data", {"job": job_dir})
            return True
        else:
            if success is False or success is None:
                return True
            else:
                pass


        """ 
        If reached to this point, the job is not disqualified yet based on requirements.
        All code above looked for disqualifying items based on day or week and after hour.
        Now check if the code should run given the requirement.
            
        For example: it may be the correct day to run the code per the requirement, but it may have already
                     been run on the day.
        """
        if requirement == "daily" or requirement in days_of_week:
            if tC.get_today_date(convert_to_string_format="%Y%m%d") == job_status["lastRunDate"]:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job does not need to run: daily requirement", {"job": job_dir})
                return False
            else:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job needs to run: daily requirement", {"job": job_dir})
                return True
        elif requirement == "hourly":
            if tC.get_today_date(convert_to_string_format="%Y%m%d") == job_status["lastRunDate"]:
                # Day is today, so check hourly
                last_hour_ran = int(job_status["lastRunHour"])
                if hour == last_hour_ran:
                    self.logging_add_event("info", "_check_if_job_needs_running",
                                           "determined job does not need to run: daily requirement", {"job": job_dir})
                    return False
                else:
                    self.logging_add_event("info", "_check_if_job_needs_running",
                                           "determined job needs to run: daily requirement", {"job": job_dir})
                    return True
            else:
                # If job has not run in the new day yet, by definition, job needs to run.
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job needs to run: daily requirement", {"job": job_dir})
                return True
        elif requirement == "weekly":
            weekly = job_status["lastRunDate"]
            if weekly is None:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job needs to run: weekly requirement", {"job": job_dir})
                return True

            temp_year = weekly[:4]
            cur_year = tC.get_current_year()

            if temp_year != cur_year:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job needs to run: weekly requirement", {"job": job_dir})
                return True

            wk_int_last_ran = tC.get_week_number_for_date(provided_date=weekly, provided_date_format="%Y%m%d")
            wk_int_today = tC.get_week_number_for_date()

            if wk_int_today == wk_int_last_ran:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job does not need to run: weekly requirement", {"job": job_dir})
                return False
            else:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job needs to run: weekly requirement", {"job": job_dir})
                return True
        elif "min" in requirement:
            diff_req = int(requirement.split(" ")[0])
            diff_act = tC.subtract_time_stamps(job_status["lastRunTimeStamp"], cur_ts)["minutes"]
            if diff_act >= diff_req:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job needs to run: minutes requirement", {"job": job_dir})
                return True
            else:
                self.logging_add_event("info", "_check_if_job_needs_running",
                                       "determined job does not need to run: minutes requirement", {"job": job_dir})
                return False

        else:
            self.logging_add_event("info", "_check_if_job_needs_running",
                                   "determined job does not need to run: no valid requirement", {"job": job_dir})
            return False

    def _write_job_status(self, job_dir, success_bool):
        job_status_file_path = osC.append_to_dir(job_dir, "jobStatus.json")
        cur_ts = tC.create_timestamp(output_format="%Y%m%d%H%M%S")
        time_components = tC.extract_date_time_components(cur_ts, input_format="%Y%m%d%H%M%S")
        month = time_components['month']
        day = time_components['day']
        hour = time_components['hour']
        minute = time_components['minute']
        second = time_components['second']

        job_status = {
            "lastRunDate": tC.get_today_date(convert_to_string_format="%Y%m%d"),
            "lastRunHour": hour,
            "lastRunMinute": minute,
            "lastRunSecond": second,
            "lastRunSuccess": success_bool,
            "lastRunMonth": month,
            "lastRunDay": day,
            "lastRunDayName": tC.get_current_day(),
            "lastRunTimeStamp": tC.create_timestamp(output_format="%Y%m%d%H%M%S")
        }

        fC.dump_json_to_file(job_status_file_path, job_status)
        self.logging_add_event("info", "_write_job_status", "updated job status",
                               {"job": job_dir, "success": success_bool})
