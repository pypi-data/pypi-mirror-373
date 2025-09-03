# coding: utf-8
from datetime import date, timedelta
from enum import Enum

from pyotrs.lib import DynamicField

from otrs_somconnexio.exceptions import TicketNotReadyToBeUpdatedWithSIMReceivedData
from otrs_somconnexio.otrs_models.process_ticket.mobile import MobileProcessTicket
from otrs_somconnexio.services.update_ticket_DF import UpdateTicketDF
from otrs_somconnexio.otrs_models.configurations.provision.mobile_ticket import (
    MobileTicketConfiguration,
    MobileTicketPausedConfiguration,
    MobileTicketCompletedConfiguration,
    MobileTicketRequestedConfiguration
)


class GetSIM(Enum):
    SIM_RECEIVED = 1
    SIM_RECEIVED_AND_DADES = 2


class SetSIMRecievedMobileTicket(UpdateTicketDF):
    """
    Set DF SIMRebuda to True to OTRS mobile tickets.
    """

    READY_QUEUES_IDS = (
        MobileTicketCompletedConfiguration.queue_id,
        MobileTicketConfiguration.queue_id,
        MobileTicketPausedConfiguration.queue_id,
        MobileTicketRequestedConfiguration.queue_id,
    )

    def __init__(
        self,
        ticket_number,
        activation_date,
        intro_date,
    ):
        self.scheduled_activation = False
        self.activation_date = activation_date
        self.intro_date = intro_date
        super().__init__(ticket_number)
        self._get_ticket()
        self.mobile_process_ticket = MobileProcessTicket(self.ticket)
        self.associated = self._has_associated_fibers()
        self.portability = self._is_portability()
        self.only_mobile = self._only_mobile()

    def _only_mobile(self):
        return self.mobile_process_ticket.service_technology != "mixta"

    def _has_associated_fibers(self):
        return bool(self.mobile_process_ticket.fiber_contract_code)

    def _is_portability(self):
        return self.mobile_process_ticket.mobile_service_type == "portabilitat"

    def _is_ready(self):
        # Si esta en las colas indicadas hacer las comprobaciones,
        # en caso contrario no hacer nada y que el cron vuelva a pasar
        if self.mobile_process_ticket.queue_id in self.READY_QUEUES_IDS:
            return True
        return False

    def _get_response(self):
        return self.scheduled_activation

    def _check_doc(self):
        return self.mobile_process_ticket.confirmed_documentation == "si"

    def _prepare_dynamic_fields(self):
        if not self._is_ready():
            raise TicketNotReadyToBeUpdatedWithSIMReceivedData(self.ticket_number)

        # Si tiene asociada y es alta nueva: Enviar SIM + Datas
        # Si tiene asociada y es portability: Enviar SIM + Datas
        # Si no tiene asociada y documentacion es true: Enviar SIM + Datas
        # Si no tiene asociada y documentacion es false: Enviar SIM
        if self.only_mobile:
            if self.associated:
                mode = GetSIM.SIM_RECEIVED_AND_DADES
            else:
                if self._check_doc():
                    mode = GetSIM.SIM_RECEIVED_AND_DADES
                else:
                    mode = GetSIM.SIM_RECEIVED
        else:
            if not self.associated and self._check_doc() and not self.portability:
                mode = GetSIM.SIM_RECEIVED_AND_DADES
            else:
                mode = GetSIM.SIM_RECEIVED

        if mode == GetSIM.SIM_RECEIVED_AND_DADES:
            self.scheduled_activation = date.today() + timedelta(days=7)
            return [
                DynamicField(name="SIMrebuda", value=1),
                DynamicField(name="permetActivacio", value="si"),
                DynamicField(
                    name="dataActivacioLiniaMobil",
                    value=str(self.activation_date),
                ),
                DynamicField(name="dataIntroPlataforma", value=str(self.intro_date)),
            ]
        elif mode == GetSIM.SIM_RECEIVED:
            return [DynamicField(name="SIMrebuda", value=1)]
