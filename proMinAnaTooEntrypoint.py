import requests
import time
import json
import socket
import main

algoName = "DPIM"
algoId = socket.gethostname()
algoIdentity = {"identification":{"name":algoName, "id":algoId}}

def serverHealthcheck():
    while True:
        try:
            healthcheck = requests.get("http://cliandanalyzer:8000/healthcheck")
            if healthcheck.status_code == 200:
                return
        except:
            time.sleep(5)

def mainEntrypoint():
    serverHealthcheck()
    stayActive = True
    while stayActive:
        instructionRequestAnswer = requests.post("http://cliandanalyzer:8000/task", json={"name":algoName, "id":algoId})
        if instructionRequestAnswer.json() != {"instruction":"no_instruction"}:
            print("Received a new instruction.", flush=True)
            print(instructionRequestAnswer.json(), flush=True)
            startInstructionHandler(instructionRequestAnswer.json())
        time.sleep(5)

def collectRequirementsForAlgo():
    epsilonR = {"name":"epsilon", "lowerBound":"0.02", "upperBound":None, "autoAdept":True, "type":"float"} #has to be > 0.01
    fit_thresholdR = {"name":"fit_threshold", "lowerBound":"0.0", "upperBound":"1.0", "autoAdept":True, "type":"float"}
    lower_boundR = {"name":"lower_bound", "lowerBound":"0", "upperBound":None, "autoAdept":False, "type":"int"}
    upper_boundR = {"name":"upper_bound", "lowerBound":"0", "upperBound":None, "autoAdept":False, "type":"int"}
    dPR = {"name":"dP", "value":"True", "type":"bool"}
    #logName = {"name":"logName", "value":"someString", "description":"This tring should be a the name of an event log.", "type":"string"}
    algoVariables = [epsilonR, fit_thresholdR, lower_boundR, upper_boundR, dPR]
    return {**algoIdentity, "inputFormat":"xes", "outputStructure":"processTree", "requirements":algoVariables}

def startInstructionHandler(instruction):
    print("Entered the instruction block.", flush=True)
    if instruction["instruction"] == "start_n_test":
        print("Accessed n_test function.", flush=True)
        requests.post("http://cliandanalyzer:8000/result/status", json={**algoIdentity, "instructionId":instruction["instructionId"], "status":"network_stable", "fileId":""})
    if instruction == {"instruction":"send_requirements"}:
        print("Accessed requirements function.", flush=True)
        jsonRequirements = collectRequirementsForAlgo()
        requests.post("http://cliandanalyzer:8000/myRequirements", json=jsonRequirements)
    if instruction["instruction"] == "comparison":
        print("Accessed Template function.", flush=True)
        algoDictionary = instruction.get("payload")
        epsilon = 1.0
        fit_threshold = 0.95
        lower_bound = 0
        upper_bound = 0
        DP = True
        for inputValues in algoDictionary["inputParameters"]:
            if inputValues["name"] == "epsilon":
                epsilon = inputValues["value"]
            if inputValues["name"] == "fit_treshold":
                fit_threshold = inputValues["value"]
            if inputValues["name"] == "lower_bound":
                lower_bound = inputValues["value"]
            if inputValues["name"] == "upper_bound":
                upper_bound = inputValues["value"]
            if inputValues["name"] == "DP":
                DP = inputValues["value"]
            if inputValues["name"] == "logName":
                logName = inputValues["value"]
        main.DPIM(epsilon, fit_threshold, lower_bound, upper_bound, DP, logName, instruction["instructionId"], algoIdentity["identification"]["id"], instruction["fileId"]).initialization()
        print("Sending the result of the template function to the server.", flush= True)
        requests.post("http://cliandanalyzer:8000/result/status", json={**algoIdentity, "instructionId":instruction["instructionId"], "status":"finished_privacy_enhancing_algorithm", "fileId":instruction["fileId"]})
    return

if __name__ == "__main__":
    mainEntrypoint()
    #DPIM(epsilonI, fit_tresholdI, lower_boundI, upper_boundI, DPI).initialization() from main.py
