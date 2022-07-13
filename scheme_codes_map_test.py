import os
import json
from mftool import Mftool
import logging
import math

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.ERROR)

mf = Mftool()

filepath = str(os.path.dirname(os.path.abspath(__file__))) + '/Scheme_to_scheme_codes_map.json'
def init_scheme_codes_map():
    with open(filepath, 'r') as f:
        return json.load(f)
scheme_codes_map = init_scheme_codes_map()

def verify_scheme_codes(perf_data):
    for scheme_cat in perf_data:
        logger.info("Scheme category is %s", scheme_cat)
        for scheme_obj in perf_data[scheme_cat]:

            # skip to next scheme category if we see this msg instead of scheme objects
            if scheme_obj == "The underlying data is unavailable for Today":
                logger.info("There's no data available for scheme category %s", scheme_cat)
                break

            # remove any trailing '#' chars and replace 'right single quotation mark' character with a simple apostrophe
            scheme_obj["scheme_name"] = scheme_obj["scheme_name"].rstrip("#").replace(u'’', u"'")
            logger.info("Scheme name is %s", scheme_obj["scheme_name"])

            # find scheme name in scheme_codes_map
            if scheme_obj["scheme_name"] in scheme_codes_map:

                ################# verify regular scheme code by comparing nav values ######################
                reg_scheme_code = scheme_codes_map[scheme_obj["scheme_name"]]["Regular"]
                # if scheme code is 0, it means regular version of this scheme is not offered in the industry
                if scheme_obj["latest NAV- Regular"] != "NA":

                    # sometimes the mf.get_scheme_quote function returns empty json
                    # try for 5 times before calling it quits
                    for x in range(0, 5):
                        reg_scheme_quote = mf.get_scheme_quote(reg_scheme_code, as_json=True)
                        # not worth retrying if we get 'None' as it means that the api did send data
                        # but it's just 'None'
                        if reg_scheme_quote == None or reg_scheme_quote != "{}":
                            break
                    # get_scheme_quote() can give None if the scheme code is invalid or is no longer active
                    if reg_scheme_quote != None:

                        logger.info("regular scheme quote is %s", type(reg_scheme_quote))
                        reg_scheme_quote = json.loads(reg_scheme_quote)
                        # compare the nav values not before removing commas and converting to floats
                        if not math.isclose(float(scheme_obj["latest NAV- Regular"].replace(',','')), float(reg_scheme_quote["nav"].replace(',',''))):
                            logger.error("Error is: data mismatch for scheme %s (regular) with scheme code %s. Data: %s - %s", scheme_obj["scheme_name"], reg_scheme_code, float(scheme_obj["latest NAV- Regular"].replace(',','')), float(reg_scheme_quote["nav"].replace(',','')))
                        else:
                            logger.info("Scheme %s (regular) scheme code verified!", scheme_obj["scheme_name"] )
                    else:
                        logger.error("Error is: invalid scheme code for scheme %s (regular)", scheme_obj["scheme_name"])
                elif reg_scheme_code != "0":
                    logger.error("Error is: scheme code is supposed to be 0 for scheme %s (regular)", scheme_obj["scheme_name"])
                else:
                    logger.info("Scheme %s (regular) doesn't exist",  scheme_obj["scheme_name"])

                ################# verify direct scheme code by comparing nav values ######################
                dir_scheme_code = scheme_codes_map[scheme_obj["scheme_name"]]["Direct"]
                # if scheme code is 0, it means direct version of this scheme is not offered in the industry
                if scheme_obj["latest NAV- Direct"] != "NA":

                    # sometimes the mf.get_scheme_quote function returns empty json
                    # try for 5 times before calling it quits
                    for x in range(0, 5):
                        dir_scheme_quote = mf.get_scheme_quote(dir_scheme_code, as_json=True)
                        # not worth retrying if we get 'None' as it means that the api did send data
                        # but it's just 'None'
                        if dir_scheme_quote == None or dir_scheme_quote != "{}":
                            break
                    # get_scheme_quote() can give None if the scheme code is invalid or is no longer active
                    if dir_scheme_quote != None:

                        logger.info("direct scheme quote is %s", type(dir_scheme_quote))
                        dir_scheme_quote = json.loads(dir_scheme_quote)
                        # compare the nav values not before removing commas and converting to floats
                        if not math.isclose(float(scheme_obj["latest NAV- Direct"].replace(',','')), float(dir_scheme_quote["nav"].replace(',',''))):
                            logger.error("Error is: data mismatch for scheme %s (direct) with scheme code %s. Data: %s - %s", scheme_obj["scheme_name"], dir_scheme_code, float(scheme_obj["latest NAV- Direct"].replace(',','')), float(dir_scheme_quote["nav"].replace(',','')))
                        else:
                            logger.info("Scheme %s (direct) scheme code verified!", scheme_obj["scheme_name"] )
                    else:
                        logger.error("Error is: invalid scheme code for scheme %s (direct)", scheme_obj["scheme_name"])
                elif dir_scheme_code != "0":
                    logger.error("Error is: scheme code is supposed to be 0 for scheme %s (direct)", scheme_obj["scheme_name"])
                else:
                    logger.info("Scheme %s (direct) doesn't exist", scheme_obj["scheme_name"])
            else:
                logger.error("Error is: Scheme name %s not found in map", scheme_obj["scheme_name"])

logger.info("Please ignore errors thrown for the following funds as the source for these funds is either pointed to incorrect scheme codes or mf.get_scheme_quote() returns 'None':")
logger.info("--- Aditya Birla Sun Life Tax Relief 96 Fund (regular)")
logger.info("--- Canara Robeco Equity Tax Saver Fund (regular)")
logger.info("--- Tata India Tax Savings Fund (regular)")
logger.info("--- Tata India Tax Savings Fund (direct)")
logger.info("---  Kotak Equity Hybrid Fund (regular)")
logger.info("--- Kotak Equity Hybrid Fund (direct)")
logger.info("--- HDFC Children's Gift Fund (regular)")
logger.info("--- HDFC Children's Gift Fund (direct)")
logger.info("--- UTI Children's Career Fund-Investment Plan (regular)")
logger.info("--- UTI Children's Career Fund-Investment Plan (direct)")
logger.info("--- UTI Children's Career Fund-Savings Plan (regular)")
logger.info("--- UTI Children's Career Fund-Savings Plan (direct)")
logger.info("--- UTI Retirement Benefit Pension Fund (regular)")
logger.info("--- UTI Retirement Benefit Pension Fund (direct)")
logger.info("--- ICICI Prudential Debt Management Fund (FOF) (direct)")
# verify scheme codes for 'equity' category schemes
perf_data = mf.get_open_ended_equity_scheme_performance(as_json=True)
verify_scheme_codes(json.loads(perf_data))

# verify scheme codes for 'debt' category schemes
perf_data = mf.get_open_ended_debt_scheme_performance(as_json=True)
verify_scheme_codes(json.loads(perf_data))

# # verify scheme codes for 'hybrid' category schemes
perf_data = mf.get_open_ended_hybrid_scheme_performance(as_json=True)
verify_scheme_codes(json.loads(perf_data))

# # verify scheme codes for 'solution' category schemes
perf_data = mf.get_open_ended_solution_scheme_performance(as_json=True)
verify_scheme_codes(json.loads(perf_data))

# # verify scheme codes of 'other' category schemes
perf_data = mf.get_open_ended_other_scheme_performance(as_json=True)
verify_scheme_codes(json.loads(perf_data))

logger.info("Verification complete!")