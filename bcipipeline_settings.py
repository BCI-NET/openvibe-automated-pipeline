# --- bcipipeline_settings.py
# Contains all settings / parameters / useful info
# that the other scripts can use

global optionKeys
optionKeys = ["",
              "PowSpectrumGraz",
              "Connectivity"]

global optionsComboText
optionsComboText = {optionKeys[0]: "",
                    optionKeys[1]: "GrazBCI - Power Spectrum Features (2 classes)",
                    optionKeys[2]: "GrazBCI - Connectivity Features"}

global optionsNbParams
optionsNbParams = {optionKeys[0]: 0,
                   optionKeys[1]: 1,
                   optionKeys[2]: 2}

global optionsTemplatesDir
optionsTemplatesDir = {optionKeys[0]: None,
                       optionKeys[1]: "spectralpower-templates",
                       optionKeys[2]: "connectivity-templates"}

global templateScenFilenames
templateScenFilenames = ["sc1-monitor-acq.xml",
                         "sc2-extract.xml",
                         "sc2-train-composite.xml",
                         "sc3-online.xml",
                         "mi-stimulations.lua"]

global pipelineAcqSettings
pipelineAcqSettings = {optionKeys[0]: None,

                       # POWER SPECTRUM
                       optionKeys[1]:
                           {"TrialNb": 20,
                            "Class1": "LEFT",
                            "Class2": "RIGHT",
                            "Baseline": 20,
                            "TrialWait": 3,
                            "TrialLength": 3,
                            "EndTrialMin": 2.5,
                            "EndTrialMax": 3.5,
                            "FeedbackLength": 3,
                            },

                       # CONNECTIVITY
                       optionKeys[2]:
                           {"TrialNb": 20,
                            "Class1": "LEFT",
                            "Class2": "RIGHT",
                            "Baseline": 20,
                            "TrialWait": 3,
                            "TrialLength": 3,
                            "EndTrialMin": 2.5,
                            "EndTrialMax": 3.5,
                            "FeedbackLength": 3,
                            }
                       }

global pipelineExtractSettings
pipelineExtractSettings = {optionKeys[0]: None,

                           # POWER SPECTRUM
                           optionKeys[1]:
                               {"StimulationEpoch": 3,
                                "StimulationDelay": 0,
                                "TimeWindowLength": 0.25,
                                "TimeWindowShift": 0.161,
                                "AutoRegressiveOrder": 19,
                                "PsdSize": 500,
                                },

                           # CONNECTIVITY
                           optionKeys[2]:
                               {"StimulationEpoch": 1.5,
                                "StimulationDelay": 0,
                                "ConnectivityMetric": "MSC",
                                "WelchLength": 4,
                                "WelchOverlap": 50,
                                "WindowMethod": "Hann",
                                "WelchWinLength": 0.25,
                                "WelchWinOverlap": 50,
                                "FftSize": 256,
                                }

                           }

global paramIdText
paramIdText = {"TrialNb": "Nb Trials per class",
               "Class1": "Class / Stimulation 1",
               "Class2": "Class / Stimulation 2",
               "Baseline": "\"Get Set\" time (s)",
               "TrialWait": "Pre-Stimulus time (s)",
               "TrialLength": "Trial duration (s)",
               "EndTrialMin": "Inter-trial interval min (s)",
               "EndTrialMax": "Inter-trial interval max (s)",
               "FeedbackLength": "Feedback time (s) (online scenario)",
               "StimulationEpoch": "Epoch of Interest (EOI) (s)",
               "StimulationDelay": "EOI offset (s)",
               "TimeWindowLength": "Sliding Window (Burg) (s)",
               "TimeWindowShift": "Overlap (Burg) (s)",
               "AutoRegressiveOrder": "AR Burg Order (samples)",
               # "AutoRegressiveOrder": "Auto-regressive estim. length (s)",
               "PsdSize": "FFT Size",
               # "PsdSize": "Frequency resolution (ratio)",
               "ConnectivityMetric": "Connectivity Metric (MSC or IMCOH)",
               "WelchLength": "Length of a Connectivity estimation (s)",
               "WelchOverlap": "Connectivity estimation overlapping (%)",
               "WindowMethod": "Welch sliding window (Hann or Hamming)",
               "WelchWinLength": "Welch sliding window length (s)",
               "WelchWinOverlap": "Welch sliding window overlap (%)",
               "ConnectFftSize": "Connectivity: FFT Size"
               }

global specialParamsDefaultDisplay
specialParamsDefaultDisplay = {"AutoRegressiveOrder": 0.038,  # in (s) assuming order = 19 and fsamp = 500
                               "PsdSize": 1,  # ratio fsamp/psdsize, assuming fsamp=500 and psdSize=500
                               }
