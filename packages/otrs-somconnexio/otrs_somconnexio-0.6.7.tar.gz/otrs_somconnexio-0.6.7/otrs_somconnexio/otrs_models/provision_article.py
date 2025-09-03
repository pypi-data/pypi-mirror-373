# coding: utf-8
from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle
from otrs_somconnexio.services.get_ticket_title import GetTicketTitle


class ProvisionArticle(AbstractArticle):
    def __init__(self, technology, order_id, service_type, notes=""):
        subject = GetTicketTitle(technology, order_id, service_type).build()
        self.subject = subject
        if notes:
            self.isVisibleForCustomer = "0"
        self.body = notes
