"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The actual user-facing chart classes are contained in this module. Each
    chart class is easily serializable using the ToJSON class. Each chart type
    is instantiated by passing an instance of Subject, apart from Transits.
    This assumes the current moment and optionally takes a pair of coordinates
    for house calculations, although these will default to those specified in
    the settings if they are not required.

    Instead of a dedicated synastry chart, the optional aspects_to parameter
    in each chart type's constructor takes another Chart instance and forms its
    aspects to the planets in that chart rather than its own. An additional
    houses_for_aspected boolean is available on the Transits chart to use the
    houses of the passed aspects_to chart.

"""

import json
from datetime import datetime
from typing import TypeVar

from immanuel.classes import wrap
from immanuel.classes.localize import localize as _
from immanuel.classes.serialize import ToJSON
from immanuel.const import calc, chart, names
from immanuel.reports import aspect, dignity, pattern, weighting
from immanuel.setup import settings
from immanuel.tools import (
    convert,
    date,
    ephemeris,
    forecast,
    midpoint,
    position,
)


ChartType = TypeVar("ChartType", bound="Chart")


class Subject:
    """Simple class to model a chart subject - essentially just
    a time and place."""

    def __init__(
        self,
        date_time: str | float | datetime,
        latitude: float | list | tuple | str,
        longitude: float | list | tuple | str,
        timezone_offset: float | None = None,
        timezone: str | None = None,
        time_is_dst: bool | None = None,
    ) -> None:
        self.latitude, self.longitude = convert.coordinates(latitude, longitude)
        self.timezone_offset = timezone_offset
        self.timezone = timezone
        self.time_is_dst = time_is_dst
        self.date_time = date.to_datetime(
            dt=date_time,
            lat=self.latitude,
            lon=self.longitude,
            offset=timezone_offset,
            time_zone=timezone,
            is_dst=time_is_dst,
        )
        self.date_time_ambiguous = (
            date.ambiguous(self.date_time) and time_is_dst is None
        )
        self.julian_date = date.to_jd(self.date_time)


class Chart:
    """Base chart class. This acts as an abstract class for the actual chart
    classes to inherit from."""

    def __init__(self, type: int, aspects_to: ChartType | None = None) -> None:
        self.type = _(names.CHART_TYPES[type])
        self._type = type
        self._aspects_to = aspects_to

        self._native: Subject
        self._obliquity: float
        self._diurnal: bool
        self._moon_phase: int
        self._triad: dict = {
            chart.SUN: None,
            chart.MOON: None,
            chart.ASC: None,
        }
        self._objects: dict
        self._houses: dict

        self.generate()
        self.wrap()

    def house_for(self, object: wrap.Object) -> int:
        """Returns the index of the house where any passed arbitrary object
        would appear in the current chart. Useful for synastries and
        transit charts."""
        return position.house(object.longitude.raw, self._houses)["index"]

    def generate(self) -> None:
        """Generating the raw data is each descendant class's
        responsibility."""
        pass

    def wrap(self) -> None:
        """Loop through the required data and wrap each one with a custom
        function."""
        for index in settings.chart_data[self._type]:
            method = f"set_wrapped_{index}"
            if hasattr(self, method):
                getattr(self, method)()

    # Base class provides wrappers for properties common to all classes.
    def set_wrapped_native(self) -> None:
        self.native = wrap.Subject(self._native)

    def set_wrapped_house_system(self) -> None:
        self.house_system = _(names.HOUSE_SYSTEMS[settings.house_system])

    def set_wrapped_shape(self) -> None:
        self.shape = _(names.CHART_SHAPES[pattern.chart_shape(self._objects)])

    def set_wrapped_diurnal(self) -> None:
        self.diurnal = self._diurnal

    def set_wrapped_moon_phase(self) -> None:
        self.moon_phase = wrap.MoonPhase(self._moon_phase)

    def set_wrapped_objects(self) -> None:
        self.objects = {}

        for index, object in self._objects.items():
            house = position.house(
                object=object,
                houses=self._houses,
            )
            out_of_bounds = ephemeris.is_out_of_bounds(
                object=object,
                obliquity=self._obliquity,
            )
            in_sect = (
                ephemeris.is_in_sect(
                    object=object,
                    is_daytime=self._diurnal,
                    sun=self._triad[chart.SUN],
                )
                if object["index"]
                in (
                    chart.SUN,
                    chart.MOON,
                    chart.MERCURY,
                    chart.VENUS,
                    chart.MARS,
                    chart.JUPITER,
                    chart.SATURN,
                )
                else None
            )
            dignity_state = (
                dignity.all(
                    object=object,
                    objects=self._objects,
                    is_daytime=self._diurnal,
                )
                if object["type"] == chart.PLANET
                and calc.PLANETS.issubset(self._objects)
                else None
            )
            date_time = (
                date.to_datetime(
                    dt=object["jd"],
                    lat=self._native.latitude,
                    lon=self._native.longitude,
                    offset=self._native.timezone_offset,
                    time_zone=self._native.timezone,
                )
                if "jd" in object
                else None
            )

            self.objects[index] = wrap.Object(
                object=object,
                date_time=date_time,
                house=house,
                out_of_bounds=out_of_bounds,
                in_sect=in_sect,
                dignity_state=dignity_state,
            )

    def set_wrapped_houses(self) -> None:
        self.houses = {
            index: wrap.Object(object=house) for index, house in self._houses.items()
        }

    def set_wrapped_aspects(self) -> None:
        aspects = (
            aspect.all(self._objects)
            if self._aspects_to is None
            else aspect.synastry(self._objects, self._aspects_to._objects)
        )
        self.aspects = {
            index: {
                object_index: wrap.Aspect(
                    aspect=object_aspect,
                    active_name=self._objects[object_aspect["active"]]["name"]
                    if object_aspect["active"] in self._objects
                    else self._aspects_to._objects[object_aspect["active"]]["name"],
                    passive_name=self._objects[object_aspect["passive"]]["name"]
                    if object_aspect["passive"] in self._objects
                    else self._aspects_to._objects[object_aspect["passive"]]["name"],
                )
                for object_index, object_aspect in aspect_list.items()
            }
            for index, aspect_list in aspects.items()
        }

    def set_wrapped_weightings(self) -> None:
        self.weightings = wrap.Weightings(
            elements=weighting.elements(self._objects),
            modalities=weighting.modalities(self._objects),
            quadrants=weighting.quadrants(self._objects, self._houses),
        )

    def to_json(self, **kwargs) -> str:
        return json.dumps(self, cls=ToJSON, **kwargs)


class Natal(Chart):
    """Standard natal chart generates data straight from the passed
    native information."""

    def __init__(self, native: Subject, aspects_to: Chart | None = None) -> None:
        self._native = native
        super().__init__(chart.NATAL, aspects_to)

    def generate(self) -> None:
        self._obliquity = ephemeris.earth_obliquity(self._native.julian_date)

        self._triad[chart.SUN] = ephemeris.get_planet(
            chart.SUN, self._native.julian_date
        )
        self._triad[chart.MOON] = ephemeris.get_planet(
            chart.MOON, self._native.julian_date
        )
        self._triad[chart.ASC] = ephemeris.get_angle(
            index=chart.ASC,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )
        self._objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = ephemeris.get_houses(
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )


class SolarReturn(Chart):
    """Solar return chart for the given year."""

    def __init__(
        self, native: Subject, year: int, aspects_to: Chart | None = None
    ) -> None:
        self._native = native
        self._solar_return_year = year
        super().__init__(chart.SOLAR_RETURN, aspects_to)

    def generate(self) -> None:
        self._solar_return_jd = forecast.solar_return(
            self._native.julian_date, self._solar_return_year
        )
        self._obliquity = ephemeris.earth_obliquity(self._solar_return_jd)
        self._solar_return_armc = ephemeris.get_angle(
            index=chart.ARMC,
            jd=self._solar_return_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

        self._triad[chart.SUN] = ephemeris.get_planet(chart.SUN, self._solar_return_jd)
        self._triad[chart.MOON] = ephemeris.get_planet(
            chart.MOON, self._solar_return_jd
        )
        self._triad[chart.ASC] = ephemeris.get_angle(
            index=chart.ASC,
            jd=self._solar_return_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )
        self._objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._solar_return_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = ephemeris.get_houses(
            jd=self._solar_return_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

    def set_wrapped_solar_return_year(self) -> None:
        self.solar_return_year = self._solar_return_year

    def set_wrapped_solar_return_date_time(self) -> None:
        self.solar_return_date_time = wrap.DateTime(
            dt=self._solar_return_jd,
            armc=self._solar_return_armc,
            latitude=self._native.latitude,
            longitude=self._native.longitude,
            offset=self._native.timezone_offset,
            timezone=self._native.timezone,
        )


class Progressed(Chart):
    """Secondary progression chart uses the MC progression method from
    settings."""

    def __init__(
        self,
        native: Subject,
        date_time: datetime | str,
        aspects_to: Chart | None = None,
    ) -> None:
        self._native = native
        self._date_time = date_time
        super().__init__(chart.PROGRESSED, aspects_to)

    def generate(self) -> None:
        self._progression_date_time = date.to_datetime(
            dt=self._date_time,
            lat=self._native.latitude,
            lon=self._native.longitude,
            offset=self._native.timezone_offset,
            time_zone=self._native.timezone,
        )
        progression_jd = date.to_jd(self._progression_date_time)
        progression_armc = ephemeris.get_angle(
            index=chart.ARMC,
            jd=progression_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )
        self._progression_armc_longitude = progression_armc["lon"]

        self._progressed_jd, self._progressed_armc_longitude = forecast.progression(
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            pjd=progression_jd,
            house_system=settings.house_system,
            method=settings.mc_progression_method,
        )
        self._obliquity = ephemeris.earth_obliquity(self._progressed_jd)

        self._triad[chart.SUN] = ephemeris.get_planet(chart.SUN, self._progressed_jd)
        self._triad[chart.MOON] = ephemeris.get_planet(chart.MOON, self._progressed_jd)
        self._triad[chart.ASC] = ephemeris.get_armc_angle(
            index=chart.ASC,
            armc=self._progressed_armc_longitude,
            lat=self._native.latitude,
            obliquity=self._obliquity,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )
        self._objects = ephemeris.get_armc_objects(
            object_list=settings.objects,
            jd=self._progressed_jd,
            armc=self._progressed_armc_longitude,
            lat=self._native.latitude,
            lon=self._native.longitude,
            obliquity=self._obliquity,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = ephemeris.get_armc_houses(
            armc=self._progressed_armc_longitude,
            lat=self._native.latitude,
            obliquity=self._obliquity,
            house_system=settings.house_system,
        )

    def set_wrapped_progression_date_time(self) -> None:
        self.progression_date_time = wrap.DateTime(
            dt=self._progression_date_time,
            armc=self._progression_armc_longitude,
        )

    def set_wrapped_progressed_date_time(self) -> None:
        self.progressed_date_time = wrap.DateTime(
            dt=self._progressed_jd,
            armc=self._progressed_armc_longitude,
            latitude=self._native.latitude,
            longitude=self._native.longitude,
            offset=self._native.timezone_offset,
            timezone=self._native.timezone,
        )

    def set_wrapped_progression_method(self) -> None:
        self.progression_method = _(
            names.PROGRESSION_METHODS[settings.mc_progression_method]
        )


class Composite(Chart):
    """Generates a midpoint chart based on the two passed sets of data."""

    def __init__(
        self, native: Subject, partner: Subject, aspects_to: Chart | None = None
    ) -> None:
        self._native = native
        self._partner = partner
        super().__init__(chart.COMPOSITE, aspects_to)

    def generate(self) -> None:
        self._obliquity = midpoint.obliquity(
            self._native.julian_date, self._partner.julian_date
        )

        native_objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        partner_objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._partner.julian_date,
            lat=self._partner.latitude,
            lon=self._partner.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._objects = midpoint.all(
            objects1=native_objects,
            objects2=partner_objects,
            obliquity=self._obliquity,
        )

        if settings.house_system == chart.WHOLE_SIGN:
            native_armc = ephemeris.get_angle(
                index=chart.ARMC,
                jd=self._native.julian_date,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
            partner_armc = ephemeris.get_angle(
                index=chart.ARMC,
                jd=self._partner.julian_date,
                lat=self._partner.latitude,
                lon=self._partner.longitude,
                house_system=settings.house_system,
            )
            armc = midpoint.composite(native_armc, partner_armc, self._obliquity)["lon"]
            latitude = (self._native.latitude + self._partner.latitude) / 2

            self._houses = ephemeris.get_armc_houses(
                armc=armc,
                lat=latitude,
                obliquity=self._obliquity,
                house_system=settings.house_system,
            )
        else:
            native_houses = ephemeris.get_houses(
                jd=self._native.julian_date,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
            partner_houses = ephemeris.get_houses(
                jd=self._partner.julian_date,
                lat=self._partner.latitude,
                lon=self._partner.longitude,
                house_system=settings.house_system,
            )
            self._houses = midpoint.all(
                objects1=native_houses,
                objects2=partner_houses,
                obliquity=self._obliquity,
            )

        if chart.ASC in self._objects:
            self._triad[chart.ASC] = self._objects[chart.ASC]
        else:
            native_asc = ephemeris.get_angle(
                index=chart.ASC,
                jd=self._native.julian_date,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
            partner_asc = ephemeris.get_angle(
                index=chart.ASC,
                jd=self._partner.julian_date,
                lat=self._partner.latitude,
                lon=self._partner.longitude,
                house_system=settings.house_system,
            )
            self._triad[chart.ASC] = midpoint.composite(
                native_asc, partner_asc, self._obliquity
            )

        if chart.SUN in self._objects:
            self._triad[chart.SUN] = self._objects[chart.SUN]
        else:
            native_sun = ephemeris.get_planet(chart.SUN, self._native.julian_date)
            partner_sun = ephemeris.get_planet(chart.SUN, self._partner.julian_date)
            self._triad[chart.SUN] = midpoint.composite(
                native_sun, partner_sun, self._obliquity
            )

        if chart.MOON in self._objects:
            self._triad[chart.MOON] = self._objects[chart.MOON]
        else:
            native_moon = ephemeris.get_planet(chart.MOON, self._native.julian_date)
            partner_moon = ephemeris.get_planet(chart.MOON, self._partner.julian_date)
            self._triad[chart.MOON] = midpoint.composite(
                native_moon, partner_moon, self._obliquity
            )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )

    def set_wrapped_partner(self):
        self.partner = wrap.Subject(self._partner)


class Transits(Chart):
    """Chart of the moment for the given coordinates. Structurally identical
    to the natal chart. Coordinates default to those specified in settings."""

    def __init__(
        self,
        latitude: float | list | tuple | str = settings.default_latitude,
        longitude: float | list | tuple | str = settings.default_longitude,
        offset: float | None = None,
        timezone: str | None = None,
        aspects_to: Chart | None = None,
        houses_for_aspected: bool = False,
    ) -> None:
        lat, lon = convert.coordinates(latitude, longitude)
        date_time = date.localize(datetime.now(), lat, lon, offset, timezone)
        self._native = Subject(date_time, lat, lon, offset, timezone)
        self._houses_for_aspected = houses_for_aspected
        super().__init__(chart.TRANSITS, aspects_to)

    def generate(self) -> None:
        self._obliquity = ephemeris.earth_obliquity(self._native.julian_date)

        self._triad[chart.SUN] = ephemeris.get_planet(
            chart.SUN, self._native.julian_date
        )
        self._triad[chart.MOON] = ephemeris.get_planet(
            chart.MOON, self._native.julian_date
        )
        self._triad[chart.ASC] = ephemeris.get_angle(
            index=chart.ASC,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )
        self._objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = (
            ephemeris.get_houses(
                jd=self._native.julian_date,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
            if self._aspects_to is None or self._houses_for_aspected is False
            else self._aspects_to._houses
        )
