########################################################################################################################
# IMPORTS

import gettext
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import pycountry
import requests
from geopy.distance import geodesic
from jellyfish import jaro_winkler_similarity

from ..params.nominatim import CITY_TO_PROVINCE, POSTCODES, STATES
from ..utils.strings import normalize

########################################################################################################################
# PARAMETERS

JARO_WINKLER_THRESHOLD = 0.85
CLOSE_KM = 2.0

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)
spanish = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["es"])
spanish.install()


class GeoNames:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def validate_postcode(postcode: Union[int, str]) -> Optional[str]:
        if isinstance(postcode, int):
            postcode = str(postcode)

        if postcode and len(postcode) == 5 and postcode[:2] in POSTCODES:
            return postcode

        if postcode and len(postcode) == 4:
            postcode = f"0{postcode}"
            if postcode[:2] in POSTCODES:
                return postcode

    @staticmethod
    def get_province_from_postcode(postcode: Optional[str]) -> Optional[str]:
        if postcode:
            return POSTCODES[postcode[:2]]

    def reverse(self, lat: Union[float, str], lon: Union[float, str]) -> Dict[str, Any]:
        return requests.get(f"{self.endpoint}/reverse?lat={lat}&lon={lon}", timeout=30).json()


class Nominatim:
    def __init__(self, nominatim_endpoint: str, geonames_endpoint: str) -> None:
        self.endpoint = nominatim_endpoint
        self.geonames = GeoNames(geonames_endpoint)

    @staticmethod
    def _get_attribute(raw_json: Dict[str, Any], keys: List[str]) -> Any:
        for key in keys:
            if key in raw_json:
                return raw_json[key]

    def _calculate_distance(
        self, lat_str: Optional[str], lon_str: Optional[str], input_coords: Tuple[float, float]
    ) -> float:
        dist = float("inf")
        if lat_str and lon_str:
            try:
                coords = (float(lat_str), float(lon_str))
                dist = geodesic(input_coords, coords).km
            except (ValueError, TypeError):
                logger.warning("Invalid coordinates for distance calculation.")
        return dist

    def _parse_nominatim_result(self, nominatim_raw_json: Dict[str, Any]) -> Dict[str, Optional[str]]:
        raw_address = nominatim_raw_json.get("address", {})

        postcode_str = str(raw_address.get("postcode", ""))
        postcode = self.geonames.validate_postcode(postcode_str)

        city = self._get_attribute(raw_address, ["city", "town", "village"])
        district, quarter = self._get_district_quarter(raw_address)

        return {
            "country": raw_address.get("country"),
            "country_code": (raw_address.get("country_code") or "").lower(),
            "state": raw_address.get("state"),
            "province": raw_address.get("province") or CITY_TO_PROVINCE.get(city),
            "city": city,
            "postcode": postcode,
            "district": district,
            "quarter": quarter,
            "street": raw_address.get("road"),
            "number": raw_address.get("house_number"),
        }

    def _parse_geonames_result(self, geonames_raw_json: Dict[str, Any]) -> Dict[str, Optional[str]]:
        geonames_country_code_str = geonames_raw_json.get("country_code")
        country_name = None
        if geonames_country_code_str:
            try:
                country_obj = pycountry.countries.get(alpha_2=geonames_country_code_str.upper())
                if country_obj:
                    country_name = spanish.gettext(country_obj.name)
            except LookupError:
                logger.warning(f"Country name not found for code: {geonames_country_code_str} using pycountry.")

        postcode_str = str(geonames_raw_json.get("postal_code", ""))
        postcode = self.geonames.validate_postcode(postcode_str)
        province = self.geonames.get_province_from_postcode(postcode) if postcode else None
        city = geonames_raw_json.get("place_name")

        return {
            "country": country_name,
            "country_code": (geonames_country_code_str or "").lower(),
            "state": geonames_raw_json.get("community"),
            "province": province,
            "city": city,
            "postcode": postcode,
            "district": None,
            "quarter": None,
            "street": None,
            "number": None,
        }

    def _get_empty_address_result(self) -> Dict[str, None]:
        return {
            "country": None,
            "country_code": None,
            "state": None,
            "province": None,
            "city": None,
            "postcode": None,
            "district": None,
            "quarter": None,
            "street": None,
            "number": None,
        }

    @staticmethod
    def _canonicalize_state(state: Optional[str]) -> Optional[str]:
        """
        Canonicalize the state name using similarity. The most similar canonical state name is
        returned if the similarity score is above the threshold.
        """
        if not state:
            return None
        norm_state = normalize(state)
        best_match = None
        best_score = 0.0
        for canonical in STATES:
            score = jaro_winkler_similarity(norm_state, normalize(canonical))
            if score > best_score:
                best_score = score
                best_match = canonical
        return best_match if best_score > JARO_WINKLER_THRESHOLD else None

    def _select_postcode_and_derived_province(
        self,
        parsed_nominatim_result: Dict[str, Optional[str]],
        parsed_geonames_result: Dict[str, Optional[str]],
        nominatim_address_province_raw: Optional[str],
        dist_nominatim: float,  # distance Nominatim ↔ input (km)
        dist_geonames: float,  # distance GeoNames ↔ input (km)
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Decide the authoritative postcode, the province derived from it and the associated state.

        Strategy:
        1. Derive province from each postcode.
        2. Validate each postcode–province pair:
        • Nominatim: compare with raw province string (if present).
        • GeoNames: multi-step validation (raw province, then Nominatim-derived
            province when Nominatim coords are close, then distance fallback).
        3. Return the postcode/province that passes validation with precedence:
        Nominatim > GeoNames. Returns (None, None, None) if neither passes.
        """

        # --- Extract postcodes ---
        nominatim_postcode = parsed_nominatim_result.get("postcode")
        geonames_postcode = parsed_geonames_result.get("postcode")

        # --- Province derived from each postcode ---
        province_from_nominatim_pc = self.geonames.get_province_from_postcode(nominatim_postcode)
        province_from_geonames_pc = self.geonames.get_province_from_postcode(geonames_postcode)

        # --- Normalised strings for similarity comparisons ---
        norm_raw_province = normalize(nominatim_address_province_raw) if nominatim_address_province_raw else ""
        norm_province_from_nominatim_pc = normalize(province_from_nominatim_pc) if province_from_nominatim_pc else ""
        norm_province_from_geonames_pc = normalize(province_from_geonames_pc) if province_from_geonames_pc else ""

        # --- Distance heuristics ---
        nominatim_is_close = dist_nominatim < CLOSE_KM
        geonames_is_close = dist_geonames < CLOSE_KM

        # --- Validate Nominatim postcode ---
        nominatim_pc_valid = False
        if norm_province_from_nominatim_pc and norm_raw_province:
            nominatim_pc_valid = (
                jaro_winkler_similarity(norm_province_from_nominatim_pc, norm_raw_province) > JARO_WINKLER_THRESHOLD
            )

        # --- Validate GeoNames postcode ---
        geonames_pc_valid = False

        # 1) Compare with raw province string (if exists)
        if norm_province_from_geonames_pc and norm_raw_province:
            geonames_pc_valid = (
                jaro_winkler_similarity(norm_province_from_geonames_pc, norm_raw_province) > JARO_WINKLER_THRESHOLD
            )

        # 2) If no raw province, compare with province from Nominatim PC **only when** Nominatim is close
        if not geonames_pc_valid and not norm_raw_province and nominatim_is_close:
            if norm_province_from_geonames_pc and norm_province_from_nominatim_pc:
                geonames_pc_valid = (
                    jaro_winkler_similarity(norm_province_from_geonames_pc, norm_province_from_nominatim_pc)
                    > JARO_WINKLER_THRESHOLD
                )

        # 3) Fallback: accept GeoNames PC if its coordinates are very close
        if not geonames_pc_valid and geonames_is_close and geonames_postcode:
            geonames_pc_valid = True

        # --- Select authoritative tuple ---
        postcode = None
        province = None
        state = None

        if nominatim_pc_valid:
            postcode = nominatim_postcode
            province = province_from_nominatim_pc
            state = parsed_nominatim_result.get("state")
            if not state and geonames_pc_valid:
                state = parsed_geonames_result.get("state")
        elif geonames_pc_valid:
            postcode = geonames_postcode
            province = province_from_geonames_pc
            state = parsed_geonames_result.get("state")
            if not state and nominatim_pc_valid:
                state = parsed_nominatim_result.get("state")

        # Canonicalize
        state = self._canonicalize_state(state)

        return postcode, province, state

    def _select_final_result(
        self,
        parsed_nominatim_result: Dict[str, Optional[str]],
        parsed_geonames_result: Dict[str, Optional[str]],
        dist_nominatim: float,
        dist_geonames: float,
        authoritative_postcode: Optional[str],
        authoritative_province_from_postcode: Optional[str],
        authoritative_state: Optional[str],
    ) -> Dict[str, Optional[str]]:
        """
        Choose the address block (Nominatim vs GeoNames) based on distance,
        then apply the authoritative postcode/province.

        Rules:
        • Pick the source with the smaller finite distance.
        • Always overwrite 'postcode' if authoritative_postcode is present.
        • Overwrite 'province' only when authoritative_province_from_postcode is not None.
        • If both distances are ∞, return an empty address.
        """

        # ------------------------------------------------------------------ #
        # 1. Decide the base address block                                  #
        # ------------------------------------------------------------------ #
        if dist_nominatim <= dist_geonames and dist_nominatim != float("inf"):
            final_result = parsed_nominatim_result
        elif dist_geonames < dist_nominatim and dist_geonames != float("inf"):
            final_result = parsed_geonames_result
        else:
            return self._get_empty_address_result()

        # ------------------------------------------------------------------ #
        # 2. Apply authoritative postcode / province                        #
        # ------------------------------------------------------------------ #
        if authoritative_postcode:
            final_result["postcode"] = authoritative_postcode

        if authoritative_province_from_postcode:
            final_result["province"] = authoritative_province_from_postcode

        if authoritative_province_from_postcode:
            final_result["state"] = authoritative_state

        return final_result

    def _get_district_quarter(self, raw_json: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        district = self._get_attribute(raw_json, ["city_district", "suburb", "borough"])
        quarter = self._get_attribute(raw_json, ["quarter", "neighbourhood"])

        if not district and quarter:
            district = quarter
            quarter = None

        return district, quarter

    def geocode(self, address: str) -> List[Dict[str, Any]]:
        return requests.get(f"{self.endpoint}/search?q={address}&format=json", timeout=30).json()

    def geocode_parsed(self, address: str) -> Optional[Dict[str, Optional[str]]]:
        results = self.geocode(address)

        if results:
            return self.reverse_parsed(results[0]["lat"], results[0]["lon"])

    def reverse(self, lat: Union[float, str], lon: Union[float, str]) -> Dict[str, Any]:
        return requests.get(f"{self.endpoint}/reverse?lat={lat}&lon={lon}&format=json", timeout=30).json()

    def reverse_parsed(self, lat: Union[float, str], lon: Union[float, str]) -> Dict[str, Optional[str]]:
        nominatim_response = self.reverse(lat, lon)
        geonames_response = self.geonames.reverse(lat, lon)

        # Initial parsing
        parsed_nominatim_result = self._parse_nominatim_result(nominatim_response)
        parsed_geonames_result = self._parse_geonames_result(geonames_response)

        # Calculate distances
        nominatim_response_lat = nominatim_response.get("lat")
        nominatim_response_lon = nominatim_response.get("lon")
        geonames_response_lat = geonames_response.get("lat")
        geonames_response_lon = geonames_response.get("lon")

        input_coords = None
        try:
            input_coords = (float(lat), float(lon))
        except (ValueError, TypeError):
            logger.error(f"Invalid input coordinates for distance calculation: lat={lat}, lon={lon}")
            return self._get_empty_address_result()

        dist_nominatim = self._calculate_distance(nominatim_response_lat, nominatim_response_lon, input_coords)
        dist_geonames = self._calculate_distance(geonames_response_lat, geonames_response_lon, input_coords)

        # Determine authoritative postcode
        nominatim_province = parsed_nominatim_result.get("province")
        selected_postcode, selected_province_from_postcode, selected_state = self._select_postcode_and_derived_province(
            parsed_nominatim_result, parsed_geonames_result, nominatim_province, dist_nominatim, dist_geonames
        )

        # Select final result
        final_result = self._select_final_result(
            parsed_nominatim_result,
            parsed_geonames_result,
            dist_nominatim,
            dist_geonames,
            selected_postcode,
            selected_province_from_postcode,
            selected_state,
        )

        return final_result


class NominatimInterface(Nominatim):
    def __init__(self, config: Dict[str, Any]) -> None:
        if "osm" in config:
            self.config = config["osm"]

            self.nominatim_endpoint = self.config["nominatim_endpoint"]
            self.geonames_endpoint = self.config["geonames_endpoint"]

            super().__init__(self.nominatim_endpoint, self.geonames_endpoint)
        else:
            logger.warning("no osm section in config")
