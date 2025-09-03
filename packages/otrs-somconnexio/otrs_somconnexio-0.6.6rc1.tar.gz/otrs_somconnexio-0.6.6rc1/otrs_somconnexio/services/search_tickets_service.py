# coding: utf-8
from pyotrs.lib import DynamicField

from otrs_somconnexio.client import OTRSClient


class SearchTicketsService:
    """
    Search by queueId, partner, states and DF OTRS tickets.
    """

    def __init__(self, configuration_class):
        """
        configuration_class: Any ticket configuration class from 'otrs-models/configurations'
        folder in this package
        """
        self.configurations = configuration_class

        if not isinstance(configuration_class, list):
            self.configurations = [configuration_class]
        else:
            self.configurations = configuration_class

    def search(self, customer_code=None, state_list=["new"], df_dct={}):
        """
        customer_code (str): filter tickets by their customer
        df_dct (dict): key, value as list of DF with which we must search
        If value is a list of values, the method will return any match
        """

        state_list = [state for state in state_list]

        otrs_client = OTRSClient()

        process_id_df = DynamicField(
            "ProcessManagementProcessID",
            search_patterns=list(map(lambda c: c.process_id, self.configurations)),
        )
        activity_id_df = DynamicField(
            "ProcessManagementActivityID",
            search_patterns=list(map(lambda c: c.activity_id, self.configurations)),
        )
        df_list = [process_id_df, activity_id_df]

        for key, value in df_dct.items():
            df_list.append(DynamicField(key, search_patterns=list(value)))

        search_args = {
            "dynamic_fields": df_list,
            "QueueIDs": list(map(lambda c: c.queue_id, self.configurations)),
            "States": state_list,
        }

        if customer_code:
            search_args["CustomerID"] = customer_code

        return otrs_client.search_tickets(**search_args)
