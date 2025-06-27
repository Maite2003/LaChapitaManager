from models.client import Client
from models.supplier import Supplier

class AgendaService:
    # ----------- CLIENTS -----------
    @staticmethod
    def get_all_clients():
        return Client.get_all()

    @staticmethod
    def add_client(name, surname="", phone="", mail=""):
        if not name.strip():
            raise ValueError("Client name cannot be empty.")
        client = Client(name=name, surname=surname, phone=phone, mail=mail)
        client.save()
        return client

    @staticmethod
    def update_client(id, name, surname="", phone="", mail=""):
        if not name.strip():
            raise ValueError("Client name cannot be empty.")
        client = Client(id=id, name=name, surname=surname, phone=phone, mail=mail)
        client.save()
        return client

    @staticmethod
    def delete_client(client_id):
        Client.delete(client_id)

    @staticmethod
    def get_client_by_id(client_id):
        if not client_id or client_id < 0:
            return None
        return Client.get_by_id(client_id)

    # ----------- SUPPLIERS -----------
    @staticmethod
    def get_all_suppliers():
        suppliers = Supplier.get_all()
        return [
            {
                "id": s.id,
                "name": s.name,
                "surname": s.surname,
                "phone": s.phone,
                "mail": s.mail
            } for s in suppliers
        ]

    @staticmethod
    def add_supplier(name, surname="", phone="", mail=""):
        if not name.strip():
            raise ValueError("Supplier name cannot be empty.")
        supplier = Supplier(name=name, surname=surname, phone=phone, mail=mail)
        supplier.save()
        return supplier

    @staticmethod
    def update_supplier(id, name, surname="", phone="", mail=""):
        if not name.strip():
            raise ValueError("Supplier name cannot be empty.")
        supplier = Supplier(id=id, name=name, surname=surname, phone=phone, mail=mail)
        supplier.save()
        return supplier

    @staticmethod
    def delete_supplier(supplier_id):
        Supplier.delete(supplier_id)

