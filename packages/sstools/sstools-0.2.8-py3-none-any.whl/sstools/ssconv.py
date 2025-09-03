from datetime import datetime
import logging
import os
import pickle

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SsConverter:
    def __init__(self):
        self._supported_rudolph_seasons = [
            2004,
            2005,
            2006,
            2007,
            2008,
            2009,
            2010,
            2011,
            2012,
            2013,
            2014,
            2015,
            2016,
            2017,
            2018,
            2019,
            2020,
            2021,
            2022,
            2023,
            2024,
            2025,
        ]
        # There is no Rudolphtabelle for 2021. 2021 bases on times swam 2019 too.
        self._rudolph_season_base = 2025  # rudolph_season_base bases on times swam the season before

        self._supported_fina_seasons = {
            "SCM": [
                2008,
                2009,
                2010,
                2011,
                2012,
                2013,
                2014,
                2015,
                2016,
                2017,
                2018,
                2019,
                2020,
                2021,
                2022,
                2023,
                2025,
            ],
            "LCM": [
                2008,
                2009,
                2010,
                2011,
                2012,
                2013,
                2014,
                2015,
                2016,
                2017,
                2018,
                2019,
                2020,
                2021,
                2022,
                2023,
                2024,
                2025,
            ],
        }
        self._fina_season_base = {
            "SCM": 2025,  # Validity Period: 1.9.YYYY-31.8.YYYY+1
            "LCM": 2025,
        }  # Validity Period: 1.1.XXXX-31.12.XXXX
        self._fina_base_table_path = os.path.join(os.path.dirname(__file__), "fina_base_times.pkl")
        self._rudolph_punkttabelle_path = os.path.join(os.path.dirname(__file__), "rudolph_punkttabelle.pkl")
        self._dict_style_styleid = {
            "50m Freestyle": "Style-1",
            "100m Freestyle": "Style-2",
            "200m Freestyle": "Style-3",
            "400m Freestyle": "Style-5",
            "800m Freestyle": "Style-6",
            "1500m Freestyle": "Style-8",
            "50m Backstroke": "Style-9",
            "100m Backstroke": "Style-10",
            "200m Backstroke": "Style-11",
            "50m Breaststroke": "Style-12",
            "100m Breaststroke": "Style-13",
            "200m Breaststroke": "Style-14",
            "50m Butterfly": "Style-15",
            "100m Butterfly": "Style-16",
            "200m Butterfly": "Style-17",
            "200m Medley": "Style-18",
            "400m Medley": "Style-19",
            "100m Medley": "Style-20",
        }

        # dictionary concerning the syle vs. styleid relation
        self._dict_styleid_style = {v: k for k, v in self._dict_style_styleid.items()}

        # Rudolph functionality
        logger.debug("Initialize rudolph functionality")
        with open(self._rudolph_punkttabelle_path, "rb") as handle:
            self._rudolph_punkttablle = pickle.load(handle)
        self._dict_style_rudolphcolumn = {
            "50m Freestyle": 0,
            "100m Freestyle": 1,
            "200m Freestyle": 2,
            "400m Freestyle": 3,
            "800m Freestyle": 4,
            "1500m Freestyle": 5,
            "50m Breaststroke": 6,
            "100m Breaststroke": 7,
            "200m Breaststroke": 8,
            "50m Butterfly": 9,
            "100m Butterfly": 10,
            "200m Butterfly": 11,
            "50m Backstroke": 12,
            "100m Backstroke": 13,
            "200m Backstroke": 14,
            "200m Medley": 15,
            "400m Medley": 16,
        }

        # Fina functionality
        logger.debug("Initialize fina functionality")
        with open(self._fina_base_table_path, "rb") as handle:
            self._finabasetimes = pickle.load(handle)

    def get_rudolphpts_from_seconds(self, gender, style, agegroup, seconds, season_base=None):
        """
        Computes interpolated rudolph points from seconds
        :param gender:  'M' or 'F'
        :type gender: str
        :param style:  e.g. '100m Freestyle'
        :type style: str
        :param agegroup:  Rudolph table is defined from 8y to 18y + open. Agegroup < 8y is limitted to agegroup 8y. Agegroup > 18 is set to open.
        :type agegroup: int or frac
        :param seconds:  times in s, swam on LCM (50m)
        :type seconds: frac ofr List[frac]
        :param season_base:
        :return: times in s, swam on LCM (50m)
        """

        if not season_base:
            season_base = self._rudolph_season_base
        season_base = int(season_base)

        seconds_type_list = True
        if not isinstance(seconds, list):
            tmp = seconds
            seconds = list()
            seconds.append(tmp)
            seconds_type_list = False

        if gender == "M":
            ageoffset = 0
        elif gender == "F":
            ageoffset = 20 * 12
        else:
            raise ValueError("unsupported gender: %s" % gender)

        if style not in self._dict_style_rudolphcolumn:
            raise ValueError('unsupported style for rudolphpoints: "%s"' % style)
        style_idx = self._dict_style_rudolphcolumn[style]

        if season_base not in self._supported_rudolph_seasons:
            raise ValueError("unsupported season: %s" % season_base)

        if agegroup < 8:
            agegroup = 8

        if agegroup > 19:
            agegroup = 19  # corresponds to 'open'
        rudolphpts = list()
        prevtime = None
        for sec in seconds:
            match = False
            for ptsIdx in range(0, 20):
                idx = ageoffset + (agegroup - 8) * 20 + ptsIdx

                curtime = self._rudolph_punkttablle[str(season_base)][idx][style_idx]
                if curtime > sec:
                    if ptsIdx == 0:
                        return 20
                    y1 = (20 - ptsIdx) - 1
                    y2 = 20 - ptsIdx
                    x1 = curtime
                    x2 = prevtime
                    x = sec
                    currudolphpts = round(
                        (y2 - y1) / (x2 - x1) * (x - x1) + y1 + 1, 1
                    )  # linear interpolation between rudolph points
                    rudolphpts.append(currudolphpts)
                    match = True
                    break
                prevtime = curtime
            if not match:
                rudolphpts.append(0)
        if not seconds_type_list:
            return rudolphpts[0]
        else:
            return rudolphpts

    def get_seconds_from_rudolphpts(self, gender, style, agegroup, rudolphpts, season_base=None):
        """
        Computes seconds from rudolphpoints
        :param gender: 'M' or 'F'
        :type gender: str
        :param style:  e.g. '100m Freestyle'
        :type style: str
        :param agegroup:  Rudolph table is defined from 8y to 18y + open. Agegroup < 8y is limitted to agegroup 8y. Agegroup > 18 is set to open.
        :type agegroup: int
        :param rudolphpts: rudolphpoints
        :param season_base
        :type rudolphpts: frac of List[frac]
        :return: times in s, swam on LCM (50m)
        :type: frac of List[frac]
        """

        if not season_base:
            season_base = self._rudolph_season_base
        season_base = int(season_base)

        rudolphpts_type_list = True
        if not isinstance(rudolphpts, list):
            tmp = rudolphpts
            rudolphpts = list()
            rudolphpts.append(tmp)
            rudolphpts_type_list = False

        if max(rudolphpts) > 20 or min(rudolphpts) < 1:
            raise ValueError("Rudolphpts must be between 1:20: %s" % rudolphpts)

        if gender == "M":
            # 1 because of header
            ageoffset = 0
        elif gender == "F":
            ageoffset = 20 * 12
        else:
            raise ValueError("unsupported gender: %s" % gender)

        if style not in self._dict_style_rudolphcolumn:
            raise ValueError('unsupported style: "%s"' % style)
        style_idx = self._dict_style_rudolphcolumn[style]

        if season_base not in self._supported_rudolph_seasons:
            raise ValueError("unsupported season: %s" % season_base)

        if agegroup < 8:
            agegroup = 8

        if agegroup > 19:
            agegroup = 19  # corresponds to 'open'
        seconds = list()

        for rudolphpt in rudolphpts:
            idx = ageoffset + (agegroup - 8) * 20 + (20 - int(rudolphpt))
            t_bottom = self._rudolph_punkttablle[str(season_base)][idx][style_idx]
            t_top = self._rudolph_punkttablle[str(season_base)][idx - 1][style_idx]
            seconds.append((t_top - t_bottom) * (rudolphpt - int(rudolphpt)) + t_bottom)

        if not rudolphpts_type_list:
            return seconds[0]
        else:
            return seconds

    def get_finapts_from_seconds(self, course, gender, style, seconds, season_base=None):
        """
        Computes fina points from seconds
        :param course: 'SCM' or 'LCM'
        :type course: str
        :param gender: 'M' or 'F'
        :type gender: str
        :param style: e.g. '100m Freestyle'
        :type style: str
        :param seconds: time in s
        :type seconds: frac of List[frac]
        :param season_base:
        :return: fina points
        :type: int or List[int]
        """

        if not ((gender == "M") or (gender == "F")):
            raise ValueError("unknown gender: %s" % gender)

        if not ((course == "SCM") or (course == "LCM")):
            raise ValueError("unknown course: %s" % course)

        if not season_base:
            season_base = self._fina_season_base[course]
        season_base = int(season_base)

        if season_base not in self._supported_fina_seasons[course]:
            raise ValueError("unsupported season: %s" % season_base)

        seconds_type_list = True
        if not isinstance(seconds, list):
            tmp = seconds
            seconds = list()
            seconds.append(tmp)
            seconds_type_list = False

        finapts = list()
        basetime = self._finabasetimes[season_base][style][gender][course]

        if not basetime:
            raise ValueError(
                'BaseTime could not be found with arguments "%s, %s, %s, %s"' % (season_base, course, gender, style)
            )

        for sec in seconds:
            finapts.append(int(1000 * (basetime / sec) ** 3))

        if not seconds_type_list:
            return finapts[0]
        else:
            return finapts

    def get_seconds_from_finapts(self, course, gender, style, finapts, season_base=None):
        """
        :param course: 'SCM' or 'LCM'
        :type course: str
        :param gender: 'M' or 'F'
        :type gender: str
        :param style: e.g. '100m Freestyle'
        :type style: str
        :param finapts: fina points [0..1000]
        :type finapts: int of List[int]
        :param season_base:
        :return: time in s
        :type: frac or List[frac]
        """

        if not ((gender == "M") or (gender == "F")):
            raise ValueError("unknown gender: %s" % gender)
        if not ((course == "SCM") or (course == "LCM")):
            raise ValueError("unknown course: %s" % course)
        if not season_base:
            season_base = self._fina_season_base[course]
        season_base = int(season_base)
        if season_base not in self._supported_fina_seasons[course]:
            raise ValueError("unsupported season: %s" % season_base)

        finapts_type_list = True
        if not isinstance(finapts, list):
            tmp = finapts
            finapts = list()
            finapts.append(tmp)
            finapts_type_list = False

        seconds = list()
        basetime = self._finabasetimes[season_base][style][gender][course]

        if not basetime:
            raise ValueError(
                'BaseTime could not be found with arguments "%s, %s, %s, %s"' % (course, gender, style, seconds)
            )

        for fina in finapts:
            seconds.append(round(1.0 / ((fina / 1000.0) ** (1 / 3.0) / basetime), 2))

        if not finapts_type_list:
            return seconds[0]
        else:
            return seconds

    def get_supported_fina_seasons(self, course):
        return self._supported_fina_seasons[course]

    def get_supported_rudolph_seasons(self):
        return self._supported_rudolph_seasons

    def get_styleid_from_style(self, style):
        return self._dict_style_styleid[style]

    def get_style_from_styleid(self, styleid):
        return self._dict_styleid_style[styleid]

    def get_available_styleids(self):
        return list(self._dict_styleid_style.keys())

    def get_available_styles(self):
        return list(self._dict_styleid_style.values())

    def get_fina_validity_period(self, course):
        if course == "SCM":
            return "1. Sept. %s - 31. Aug. %s" % (self._fina_season_base[course], self._fina_season_base[course] + 1)
        elif course == "LCM":
            return "1. Jan. %s - 31. Dec. %s" % (self._fina_season_base[course], self._fina_season_base[course])
        return None

    def get_fina_season_base(self, course):
        return self._fina_season_base[course]

    def get_rudolph_season_base(self):
        return self._rudolph_season_base

    def set_fina_season_base(self, course, season):
        if season not in self._supported_fina_seasons[course]:
            raise ValueError("unsupported season: %s" % season)
        self._fina_season_base[course] = season

    def set_rudolph_season_base(self, season):
        if season not in self._supported_rudolph_seasons:
            raise ValueError("unsupported season: %s" % season)
        self._rudolph_season_base = season

    @staticmethod
    def get_agegroup_json_from_agegroup_url(agegroup_url):
        strlist = agegroup_url.split("_")
        if strlist[0] == "x" and strlist[0] == "x":
            return "Open"
        if strlist[0] == strlist[1]:
            return strlist[0]
        raise ValueError("not convertable %s" % agegroup_url)

    @staticmethod
    def get_agegroup_str_from_agegroup_url(agegroup_url):
        selected_athletes_places = agegroup_url.split("_")
        agegroup_str = agegroup_url.replace("_", "-") + "y"
        if len(selected_athletes_places) == 2:
            if selected_athletes_places[0] == selected_athletes_places[1]:
                if selected_athletes_places[0] == "x":
                    agegroup_str = "open"
                else:
                    agegroup_str = selected_athletes_places[0] + "y"
            if selected_athletes_places[1] != "x" and int(selected_athletes_places[1]) > 20:
                agegroup_str += " Masters"
        return agegroup_str.replace("x", "")

    @staticmethod
    def get_agegroup_url_from_agegroup_json(agegroup_json):
        strlist = agegroup_json.split("-")
        for idx in list(range(len(strlist))):
            strlist[idx] = strlist[idx].strip()
            if strlist[idx] == "":
                strlist[idx] = "x"

        if len(strlist) > 1:
            return "%s_%s" % (strlist[0], strlist[1])
        if strlist[0] == "Open":
            return "x_x"

        return "%s_%s" % (strlist[0], strlist[0])

    @staticmethod
    def get_year_fraction_from_datetime(date_in):
        # not ultimatively accurate as it does not take leap years into account
        return (float(date_in.strftime("%j")) - 1) / 366 + float(date_in.strftime("%Y"))

    @staticmethod
    def get_year_fraction_from_ssdate(ssdate):
        date = datetime.strptime(ssdate, "%Y-%m-%d")
        # not ultimatively accurate as it does not take leap years into account
        return (float(date.strftime("%j")) - 1) / 366 + float(date.strftime("%Y"))

    @staticmethod
    def get_year_fraction_from_today():
        date = datetime.today()
        # not ultimatively accurate as it does not take leap years into account
        return (float(date.strftime("%j")) - 1) / 366 + float(date.strftime("%Y"))

    @staticmethod
    def get_seconds_from_swimtime(swimtime):
        """
        convert swimtime into seconds
        :param swimtime: swim time
        :return: seconds
        """
        if not isinstance(swimtime, list):
            parts = swimtime.split(":")  # Split by colon to check the format
            if len(parts) == 1:  # Format: %S.%f
                seconds = float(parts[0])
            elif len(parts) == 2:  # Format: %M:%S.%f
                minutes, seconds = map(float, parts)
                seconds += minutes * 60
            elif len(parts) == 3:  # Format: %H:%M:%S.%f
                hours, minutes, seconds = map(float, parts)
                seconds += minutes * 60 + hours * 3600
            else:
                raise ValueError("Invalid time format")
            return seconds
        else:
            swimtimes_sec = list()
            for entry in swimtime:
                parts = entry.split(":")  # Split by colon to check the format
                if len(parts) == 1:  # Format: %S.%f
                    seconds = float(parts[0])
                elif len(parts) == 2:  # Format: %M:%S.%f
                    minutes, seconds = map(float, parts)
                    seconds += minutes * 60
                elif len(parts) == 3:  # Format: %H:%M:%S.%f
                    hours, minutes, seconds = map(float, parts)
                    seconds += minutes * 60 + hours * 3600
                else:
                    raise ValueError("Invalid time format")
                swimtimes_sec.append(seconds)
            return swimtimes_sec


ssconv = SsConverter()

if __name__ == "__main__":
    ssconv = SsConverter()
    print(ssconv.get_seconds_from_swimtime("1:23.45"))

    # print(ssconv.get_rudolphpts_from_seconds("F", "50m Butterfly", 5, 26.15, 2016))
    # print(ssconv.get_seconds_from_rudolphpts("F", "50m Butterfly", 5, 20, 2016))

    print(ssconv.get_rudolphpts_from_seconds("M", "50m Freestyle", 16, 24.73, 2024))
    print(ssconv.get_seconds_from_rudolphpts("M", "50m Freestyle", 16, 13.9, 2024))

    # print(ssconv.get_rudolphpts_from_seconds("M", "200m Freestyle", 13, 134.41, 2024))
    # print(ssconv.get_seconds_from_rudolphpts("M", "200m Freestyle", 13, 10, 2024))

    print(ssconv.get_finapts_from_seconds("LCM", "M", "1500m Freestyle", 16 * 60 + 45.63, 2024))
    print(ssconv.get_seconds_from_finapts("LCM", "M", "1500m Freestyle", 649, 2024))

    print(ssconv.get_finapts_from_seconds("LCM", "M", "1500m Freestyle", 14 * 60 + 30.67, 2025))
    print(ssconv.get_seconds_from_finapts("LCM", "M", "1500m Freestyle", 1000, 2025))

    print(ssconv.get_finapts_from_seconds("LCM", "M", "1500m Freestyle", 21 * 60 + 40.60, 2025))
    print(ssconv.get_seconds_from_finapts("LCM", "M", "1500m Freestyle", 300, 2025))

    print(ssconv.get_rudolphpts_from_seconds("M", "50m Backstroke", 16, 26.54, 2025))

    # print(ssconv.get_finapts_from_seconds("LCM", "M", "50m Freestyle", [23.96], 2009))
    # print(ssconv.get_finapts_from_seconds("LCM", "M", "100m Breaststroke", [56.88]))
    # print(ssconv.get_rudolphpts_from_seconds("F", "200m Backstroke", 9, [203.87], 2024))
    # print(ssconv.get_seconds_from_finapts("LCM", "M", "100m Freestyle", 900))
    # print(ssconv.get_finapts_from_seconds("SCM", "M", "50m Freestyle", [20.24], 2020))

    # print(ssconv.get_finapts_from_seconds("LCM", "F", "200m Freestyle", 112.98))

    # ssconv.set_fina_season_base("SCM", 2024)
    # ssconv.set_fina_season_base("LCM", 2024)
    # ssconv.set_rudolph_season_base(2024)
