import random

positive_broadcast = {
        "class": "BroadcastEvent",
        "Broadcast_Event": "TestedPositive"
        }


def add_diagnostic_survey(cb, coverage=1, repetitions=1, tsteps_btwn=365, target='Everyone', start_day=0,
                          diagnostic_type='NewDetectionTech', diagnostic_threshold=40, event_name="Diagnostic Survey",
                          nodes={"class": "NodeSetAll"}, positive_diagnosis_configs=[],
                          received_test_event='Received_Test', IP_restrictions=[], NP_restrictions=[],
                          pos_diag_IP_restrictions=[], trigger_condition_list=[], listening_duration=-1, triggered_campaign_delay=0 ):
    """
    Function to add recurring prevalence surveys with configurable diagnostic
    When using "trigger_condition_list", the diagnostic is triggered by the words listed

    :param cb: Configuration builder holding the interventions
    :param repetitions: Number of repetitions
    :param tsteps_btwn:  Timesteps between repetitions
    :param target: Target demographic. Default is 'Everyone'
    :param start_day: Start day for the outbreak
    :param coverage: probability an individual receives the diagnostic
    :param diagnostic_type: 
    :param diagnostic_threshold: sensitivity of diagnostic in parasites per uL
    :param nodes: nodes to target.
    # All nodes: {"class": "NodeSetAll"}.
    # Subset of nodes: {"class": "NodeSetNodeList", "Node_List": list_of_nodeIDs}
    :param positive_diagnosis_configs: list of events to happen to individual who receive a positive result from test
    :param received_test_event: string for individuals to broadcast upon receiving diagnostic
    :param IP_restrictions: list of IndividualProperty restrictions to restrict who takes action upon positive diagnosis
    :param NP_restrictions: node property restrictions
    :param trigger_condition_list: list of strings that will trigger a diagnostic survey.
    :param listening_duration: for diagnostics that are listening for trigger_condition_list, how long after start day to stop listening for the event
    :param triggered_campaign_delay: delay of running the campaign/intervention after receiving a trigger from the trigger_condition_list
    :return: nothing
    """

    intervention_cfg = {
                        "Diagnostic_Type": diagnostic_type, 
                        "Detection_Threshold": diagnostic_threshold, 
                        "class": "MalariaDiagnostic"                                          
                        }

    if not positive_diagnosis_configs :
        intervention_cfg["Event_Or_Config"] = "Event"
        intervention_cfg["Positive_Diagnosis_Event"] = "TestedPositive"    
    else :
        intervention_cfg["Event_Or_Config"] = "Config"
        intervention_cfg["Positive_Diagnosis_Config"] = { 
            "Intervention_List" : positive_diagnosis_configs + [positive_broadcast] ,
            "class" : "MultiInterventionDistributor" 
            }
        if pos_diag_IP_restrictions :
            intervention_cfg["Positive_Diagnosis_Config"]["Property_Restrictions_Within_Node"] = pos_diag_IP_restrictions

    if trigger_condition_list:
        sorta_unique_id = random.randrange(10000)
        for repetition in range(0, repetitions):
            # set up trigger event that triggers every person to send out the the trigger for the repetition's listeners
            if repetition == 0 and repetitions > 1:
                trigger_event = {
                    "class": "CampaignEvent",
                    "Start_Day": start_day,
                    "Nodeset_Config": nodes,
                    "Event_Coordinator_Config": {
                        "class": "StandardInterventionDistributionEventCoordinator",
                        "Intervention_Config": {
                            "class": "NodeLevelHealthTriggeredIV",
                            "Trigger_Condition_List": trigger_condition_list,
                            "Duration": listening_duration,
                            "Target_Residents_Only": 1,
                            "Actual_IndividualIntervention_Config": {
                                "class": "MultiInterventionDistributor",
                                "Intervention_List": []
                            }
                        }
                    }
                }
                for x in range(1, repetitions):
                    delayed_later_event_trigger = {
                        "class": "DelayedIntervention",
                        "Delay_Distribution": "FIXED_DURATION",
                        "Delay_Period": triggered_campaign_delay + tsteps_btwn * x,
                        "Actual_IndividualIntervention_Configs":
                            [
                                {
                                    "class": "BroadcastEvent",
                                    "Broadcast_Event": str(sorta_unique_id) + "_" + str(x)
                                }
                            ]
                    }
                    trigger_event['Event_Coordinator_Config']['Intervention_Config'][
                        "Actual_IndividualIntervention_Config"]["Intervention_List"].append(delayed_later_event_trigger)

                cb.add_event(trigger_event)

            survey_event = {"class": "CampaignEvent",
                            "Start_Day": start_day,
                            "Event_Name": event_name,
                            "Nodeset_Config": nodes,
                            "Event_Coordinator_Config": {
                                "class": "StandardInterventionDistributionEventCoordinator",
                                "Number_Distributions": -1,
                                "Intervention_Config":
                                    {
                                        "class": "NodeLevelHealthTriggeredIV",
                                        "Blackout_On_First_Occurrence": 1,
                                        "Trigger_Condition_List": trigger_condition_list,
                                        "Target_Residents_Only": 1,
                                        "Duration": listening_duration,
                                        "Demographic_Coverage": coverage,
                                        "Actual_IndividualIntervention_Config":
                                            {
                                                "class": "DelayedIntervention",
                                                "Delay_Distribution": "FIXED_DURATION",
                                                "Delay_Period": triggered_campaign_delay,
                                                "Actual_IndividualIntervention_Configs":
                                                    [
                                                        {
                                                            "class": "MultiInterventionDistributor",
                                                            "Intervention_List": [
                                                                {
                                                                 "class": "BroadcastEvent",
                                                                 "Broadcast_Event": received_test_event
                                                                },
                                                                  intervention_cfg
                                                            ]

                                                        }
                                                    ]
                                            }
                                     },
                                }
                            }
            if repetitions > 1:
                if repetition > 0:
                    survey_event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] = [
                        str(sorta_unique_id) + "_" + str(repetition)]

            if IP_restrictions:
                survey_event['Event_Coordinator_Config']['Intervention_Config']["Property_Restrictions_Within_Node"] = IP_restrictions

            if NP_restrictions:
                survey_event['Event_Coordinator_Config']['Intervention_Config']['Node_Property_Restrictions'] = NP_restrictions

            if isinstance(target, dict) and all([k in target.keys() for k in ['agemin', 'agemax']]):
                survey_event["Event_Coordinator_Config"]['Intervention_Config'].update({
                    "Target_Demographic": "ExplicitAgeRanges",
                    "Target_Age_Min": target['agemin'],
                    "Target_Age_Max": target['agemax']})
            else:
                survey_event["Event_Coordinator_Config"]['Intervention_Config'].update({
                    "Target_Demographic": target})  # default is Everyone

            cb.add_event(survey_event)

    else:
        survey_event = { "class" : "CampaignEvent",
                         "Start_Day": start_day,
                         "Event_Name" : event_name,
                         "Event_Coordinator_Config": {
                             "class": "StandardInterventionDistributionEventCoordinator",
                             "Number_Distributions": -1,
                             "Number_Repetitions": repetitions,
                             "Timesteps_Between_Repetitions": tsteps_btwn,
                             "Demographic_Coverage": coverage,
                             "Intervention_Config": {
                                 "Intervention_List" : [
                                     { "class": "BroadcastEvent",
                                     "Broadcast_Event": received_test_event },
                                      intervention_cfg ] ,
                                "class" : "MultiInterventionDistributor" }
                             },
                         "Nodeset_Config": nodes
                         }

        if IP_restrictions :
            survey_event['Event_Coordinator_Config']["Property_Restrictions_Within_Node"] = IP_restrictions

        if NP_restrictions:
            survey_event['Event_Coordinator_Config']['Node_Property_Restrictions'] = NP_restrictions

        if isinstance(target, dict) and all([k in target.keys() for k in ['agemin','agemax']]) :
            survey_event["Event_Coordinator_Config"].update({
                    "Target_Demographic": "ExplicitAgeRanges",
                    "Target_Age_Min": target['agemin'],
                    "Target_Age_Max": target['agemax'] })
        else :
            survey_event["Event_Coordinator_Config"].update({
                    "Target_Demographic": target } ) # default is Everyone
        cb.add_event(survey_event)
    return
