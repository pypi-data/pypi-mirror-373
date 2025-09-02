import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from calendar import monthrange
import httpx
import base64
from functools import partial


class PayarcConnectException(Exception):
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code


class Payarc:
    url_map = {
        'prod': 'https://api.payarc.net',
        'sandbox': 'https://testapi.payarc.net'
    }

    def __init__(self, bearer_token, base_url='sandbox', api_version='/v1/', version='1.0', bearer_token_agent=None):
        if not bearer_token:
            raise ValueError('Bearer token is required')

        self.bearer_token = bearer_token
        self.version = version
        self.base_url = self.url_map.get(base_url, base_url)
        self.base_url = f"{self.base_url}/v1/" if api_version == '/v1/' else f"{self.base_url}/v{api_version.strip('/')}/"
        self.bearer_token_agent = bearer_token_agent

        self.payarc_connect_base_url = 'https://payarcconnectapi.curvpos.com' if base_url == 'prod' else 'https://payarcconnectapi.curvpos.dev'
        self.payarc_connect_access_token = ""

        self.charges = {
            'create': self.__create_charge,
            'retrieve': self.__get_charge,
            'list': self.__list_charge,
            'agent': {
                'list': self.__list_agent_charges,
            },
            'create_refund': self.__refund_charge
        }
        self.customers = {
            'create': self.__create_customer,
            'retrieve': self.__retrieve_customer,
            'list': self.__list_customers,
            'update': self.__update_customer,
            'delete': self.__delete_customer,
        }
        self.applications = {
            'create': self.__add_lead,
            'status': self.__lead_status,
            'list': self.__apply_apps,
            'retrieve': self.__retrieve_applicant,
            'update': self.__update_applicant,
            'delete': self.__delete_applicant,
            'add_document': self.__add_applicant_document,
            'submit': self.__submit_applicant_for_signature,
            'delete_document': self.__delete_applicant_document,
            'list_sub_agents': self.__sub_agents
        }
        self.split_campaigns = {
            'create': self.__create_campaign,
            'list': self.__list_campaigns,
            'retrieve': self.__get_campaign,
            'update': self.__update_campaign,
            'list_accounts': self.__list_campaign_accounts,
        }
        self.billing = {
            'plan': {
                'create': self.__create_plan,
                'list': self.__list_plans,
                'retrieve': self.__get_plan,
                'update': self.__update_plan,
                'delete': self.__delete_plan,
                'create_subscription': self.__create_subscription,
                'subscription': {
                    'cancel': self.__cancel_subscription,
                    'update': self.__update_subscription,
                    'list': self.__list_subscriptions
                }
            }
        }
        self.disputes = {
            'list': self.__list_cases,
            'retrieve': self.__get_case,
            'add_document': self.__add_document_case
        }
        self.deposits = {
            'list': self.__list_agent_deposits,
            # 'retrieve': self.__get_merchant_deposit,
        }
        self.payarcConnect = {
            'login': self.__login,
            'sale': self.__sale,
            'void': self.__void,
            'refund': self.__refund,
            'blind_credit': self.__blind_credit,
            'auth': self.__auth,
            'post_auth': self.__post_auth,
            'last_transaction': self.__last_transaction,
            'server_info': self.__server_info,
            'terminals': self.__terminals,
        }

    def request_headers(self, token, **args):
        return {
            'Authorization': f"Bearer {token}",
            'User-Agent': f"sdk-python/{self.version}",
            **args
        }

    async def __create_charge(self, obj, charge_data=None):
        try:
            charge_data = charge_data or obj
            if 'source' in charge_data:
                source = charge_data.pop('source')
                if isinstance(source, dict) and source:
                    charge_data.update(source)
                else:
                    charge_data['source'] = source

            if obj and 'object_id' in obj:
                charge_data['customer_id'] = obj['object_id'][4:] if obj['object_id'].startswith('cus_') else obj[
                    'object_id']

            if 'source' in charge_data and charge_data['source'].startswith('tok_'):
                charge_data['token_id'] = charge_data['source'][4:]
            elif 'source' in charge_data and charge_data['source'].startswith('cus_'):
                charge_data['customer_id'] = charge_data['source'][4:]
            elif 'source' in charge_data and charge_data['source'].startswith('card_'):
                charge_data['card_id'] = charge_data['source'][5:]
            elif ('source' in charge_data and charge_data['source'].startswith('bnk_')) or 'sec_code' in charge_data:
                if 'source' in charge_data and charge_data['source'].startswith('bnk_'):
                    charge_data['bank_account_id'] = charge_data['source'][4:]
                    del charge_data['source']
                if 'bank_account_id' in charge_data and charge_data['bank_account_id'].startswith('bnk_'):
                    charge_data['bank_account_id'] = charge_data['bank_account_id'][4:]
                charge_data['type'] = 'debit'
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{self.base_url}achcharges", json=charge_data,
                                                 headers=self.request_headers(self.bearer_token))
                    response.raise_for_status()
            elif charge_data.get('source', '').isdigit():
                charge_data['card_number'] = charge_data['source']

            if 'token_id' in charge_data and charge_data['token_id'].startswith('tok_'):
                charge_data['token_id'] = charge_data['token_id'][4:]
            if 'customer_id' in charge_data and charge_data['customer_id'].startswith('cus_'):
                charge_data['customer_id'] = charge_data['customer_id'][4:]
            if 'card_id' in charge_data and charge_data['card_id'].startswith('card_'):
                charge_data['card_id'] = charge_data['card_id'][5:]

            if 'source' in charge_data:
                del charge_data['source']
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}charges", json=charge_data,
                                             headers=self.request_headers(self.bearer_token))
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Create Charge'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Create Charge'}, str(error)))
        else:
            return self.add_object_id(response.json()['data'])

    async def __get_charge(self, charge_id):
        try:
            async with httpx.AsyncClient() as client:
                if charge_id.startswith('ch_'):
                    charge_id = charge_id[3:]
                    response = await client.get(
                        f"{self.base_url}charges/{charge_id}",
                        headers=self.request_headers(self.bearer_token),
                        params={'include': 'transaction_metadata,extra_metadata'}
                    )
                elif charge_id.startswith('ach_'):
                    charge_id = charge_id[4:]
                    response = await client.get(
                        f"{self.base_url}achcharges/{charge_id}",
                        headers=self.request_headers(self.bearer_token),
                        params={'include': 'review'}
                    )
                else:
                    return []

                response.raise_for_status()

        except httpx.HTTPError as error:
            raise Exception(self.manage_error({'source': 'API Retrieve Charge Info'},
                                              error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Retrieve Charge Info'}, str(error)))
        else:
            return self.add_object_id(response.json()['data'])

    async def __list_charge(self, search_data=None):
        if search_data is None:
            search_data = {}

        limit = search_data.get('limit', 25)
        page = search_data.get('page', 1)
        search = search_data.get('search', {})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}charges",
                    headers=self.request_headers(self.bearer_token),
                    params={**{'limit': limit, 'page': page}, **search}
                )

            # Apply the object_id transformation to each charge
            charges = [self.add_object_id(charge) for charge in response.json()['data']]
            pagination = response.json().get('meta', {}).get('pagination', {})
            pagination.pop('links', None)

            response.raise_for_status()
        except httpx.HTTPError as error:
            raise Exception(self.manage_error({'source': 'API List charges'},
                                              error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API List charges'}, str(error)))
        else:
            return {'charges': charges, 'pagination': pagination}

    async def __refund_charge(self, charge, params=None):
        ach_regular = False
        if isinstance(charge, dict):
            charge_id = charge.get('object_id', charge)
        else:
            charge_id = charge

        if charge_id.startswith('ch_'):
            charge_id = charge_id[3:]

        if charge_id.startswith('ach_'):
            ach_regular = True
            response = await self.__refund_ach_charge(charge, params)
            response.raise_for_status()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}charges/{charge_id}/refunds",
                    json=params,
                    headers=self.request_headers(self.bearer_token)
                )
            response.raise_for_status()

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Refund a charge'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API List charges'}, str(error)))
        else:
            return self.add_object_id(response.json().get('data')) if not ach_regular else response

    async def __refund_ach_charge(self, charge, params=None):
        if params is None:
            params = {}

        if isinstance(charge, dict):
            # charge is already an object
            pass
        else:
            charge = await self.__get_charge(charge)  # charge will become an object

        params['type'] = 'credit'
        params['amount'] = params.get('amount', charge.get('amount'))
        params['sec_code'] = params.get('sec_code', charge.get('sec_code'))

        if charge.get('bank_account') and charge['bank_account'].get('data') and charge['bank_account']['data'].get(
                'object_id'):
            params['bank_account_id'] = params.get('bank_account_id', charge['bank_account']['data']['object_id'])

        if 'bank_account_id' in params and params['bank_account_id'].startswith('bnk_'):
            params['bank_account_id'] = params['bank_account_id'][4:]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}achcharges",
                    json=params,
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()

        except httpx.HTTPError as error:
            raise Exception(self.manage_error({'source': 'API Refund ACH Charge'},
                                              error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Refund ACH Charge'}, str(error)))
        else:
            return self.add_object_id(response.json().get('data'))

    async def __create_customer(self, customer_data=None):
        if customer_data is None:
            customer_data = {}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}customers",
                    json=customer_data,
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
                customer = self.add_object_id(response.json()['data'])

                if 'cards' in customer_data and customer_data['cards']:
                    card_token_promises = [self.__gen_token_for_card(card_data) for card_data in customer_data['cards']]
                    card_tokens = await asyncio.gather(*card_token_promises)

                    if card_tokens:
                        attached_cards_promises = [
                            self.__update_customer(customer['customer_id'], {'token_id': token['id']})
                            for token in card_tokens
                        ]
                        await asyncio.gather(*attached_cards_promises)
                        return await self.__retrieve_customer(customer['object_id'])

        except httpx.HTTPError as error:
            raise Exception(self.manage_error({'source': 'API Create customers'},
                                              error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Create customers'}, str(error)))
        else:
            return customer

    async def __retrieve_customer(self, customer_id):
        if customer_id.startswith('cus_'):
            customer_id = customer_id[4:]
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}customers/{customer_id}",
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API retrieve customer info'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API retrieve customer info'}, str(error)))
        else:
            return self.add_object_id(response.json()['data'])

    async def __gen_token_for_card(self, token_data=None):
        if token_data is None:
            token_data = {}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}tokens",
                    json=token_data,
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise Exception(self.manage_error({'source': 'API for tokens'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API for tokens'}, str(error)))
        else:
            return response.json()['data']

    async def __add_card_to_customer(self, customer_id, card_data):
        try:
            customer_id = customer_id.get('object_id', customer_id)
            if customer_id.startswith('cus_'):
                customer_id = customer_id[4:]

            card_token = await self.__gen_token_for_card(card_data)
            attached_cards = await self.__update_customer(customer_id, {'token_id': card_token['id']})
        except httpx.HTTPError as error:
            return self.manage_error({'source': 'API add card to customer'}, error.response if error.response else {})
        except Exception as error:
            return self.manage_error({'source': 'API add card to customer'}, str(error))
        else:
            return self.add_object_id(card_token['card']['data'])

    async def __add_bank_acc_to_customer(self, customer_id, acc_data):
        try:
            customer_id = customer_id.get('object_id', customer_id)
            if customer_id.startswith('cus_'):
                customer_id = customer_id[4:]

            acc_data['customer_id'] = customer_id
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}bankaccounts",
                    json=acc_data,
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()

        except httpx.HTTPError as error:
            raise Exception(self.manage_error({'source': 'API BankAccount to customer'},
                                              error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API BankAccount to customer'}, str(error)))
        else:
            return self.add_object_id(response.json()['data'])

    async def __list_customers(self, search_data=None):
        if search_data is None:
            search_data = {}

        limit = search_data.get('limit', 25)
        page = search_data.get('page', 1)
        constraint = search_data.get('constraint', {})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}customers",
                    headers=self.request_headers(self.bearer_token),
                    params={'limit': limit, 'page': page, **constraint}
                )
                response.raise_for_status()
                response_data = response.json()
                # Apply the object_id transformation to each customer
                customers = [self.add_object_id(customer) for customer in response_data['data']]
                pagination = response_data.get('meta', {}).get('pagination', {})
                pagination.pop('links', None)
                return {'customers': customers, 'pagination': pagination}

        except httpx.HTTPError as http_error:
            error_response = http_error.response if http_error.response else {}
            raise Exception(self.manage_error({'source': 'API List customers'}, error_response))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API List customers'}, str(error)))

    async def __update_customer(self, customer, cust_data):
        if 'object_id' in customer:
            customer = customer['object_id']
        if customer.startswith('cus_'):
            customer = customer[4:]
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}customers/{customer}",
                    json=cust_data,
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API update customer info'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API update customer info'}, str(error)))
        else:
            return self.add_object_id(response.json()['data'])

    async def __delete_customer(self, customer):
        if 'object_id' in customer:
            customer = customer['object_id']
        if customer.startswith('cus_'):
            customer = customer[4:]
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}customers/{customer}",
                    headers=self.request_headers(self.bearer_token)
                )
                if response.status_code == 204:
                    return {}
                response.raise_for_status()
                return self.add_object_id(response.json().get('data', {}))
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API delete customer'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API delete customer'}, str(error)))

    async def __add_lead(self, applicant):
        if 'agentId' in applicant and applicant['agentId'].startswith('usr_'):
            applicant['agentId'] = applicant['agentId'][4:]
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}agent-hub/apply/add-lead",
                    json=applicant,
                    headers=self.request_headers(self.bearer_token_agent)
                )
                response.raise_for_status()
                return self.add_object_id(response.json())
        except httpx.HTTPError as error:
            raise Exception(self.manage_error({'source': 'API add lead'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API add lead'}, str(error)))

    async def __lead_status(self, applicant):
        try:
            if isinstance(applicant, dict):
                applicant_id = applicant.get('object_id', applicant)
            else:
                applicant_id = applicant
            if applicant_id.startswith('appl_'):
                applicant_id = applicant_id[5:]
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}agent-hub/apply/lead-status",
                    json={'MerchantCode': applicant_id},
                    headers=self.request_headers(self.bearer_token_agent)
                )
                response.raise_for_status()
                applicant_data = response.json()
                return self.add_object_id(applicant_data)

        except httpx.HTTPError as http_error:
            error_response = http_error.response if http_error.response else {}
            raise Exception(self.manage_error({'source': 'API lead status'}, error_response))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API lead status'}, str(error)))

    async def __apply_apps(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}agent-hub/apply-apps",
                    headers=self.request_headers(self.bearer_token_agent),
                    params={
                        'limit': 0,
                        'is_archived': 0
                    }
                )
                response.raise_for_status()
                response_data = response.json()
                applications = [self.add_object_id(application) for application in response_data['data']]
                pagination = response_data.get('meta', {}).get('pagination', {})
                pagination.pop('links', None)
                return {'applications': applications, 'pagination': pagination}

        except httpx.HTTPError as http_error:
            error_response = http_error.response if http_error.response else {}
            raise Exception(self.manage_error({'source': 'API list Apply apps'}, error_response))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API list Apply apps'}, str(error)))

    async def __retrieve_applicant(self, applicant):
        try:
            if isinstance(applicant, dict):
                applicant_id = applicant.get('object_id', applicant)
            else:
                applicant_id = applicant
            if applicant_id.startswith('appl_'):
                applicant_id = applicant_id[5:]

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}agent-hub/apply-apps/{applicant_id}",
                    headers=self.request_headers(self.bearer_token_agent),
                    params={}
                )
                response.raise_for_status()
                applicant_data = response.json()

                docs_response = await client.get(
                    f"{self.base_url}agent-hub/apply-documents/{applicant_id}",
                    headers=self.request_headers(self.bearer_token_agent),
                    params={'limit': 0}
                )
                docs_response.raise_for_status()
                docs_data = docs_response.json()

                docs_data.pop('meta', None)
                applicant_data.pop('meta', None)
                applicant_data['Documents'] = docs_data
                if 'object' not in applicant_data['data']:
                    applicant_data['data']['object'] = 'ApplyApp'
                return self.add_object_id(applicant_data)

        except httpx.HTTPError as http_error:
            error_response = http_error.response if http_error.response else {}
            raise Exception(self.manage_error({'source': 'API Apply apps status'}, error_response))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Apply apps status'}, str(error)))

    async def __delete_applicant(self, applicant):
        if isinstance(applicant, dict):
            applicant_id = applicant.get('object_id', applicant)
        else:
            applicant_id = applicant
        try:
            if applicant_id.startswith('appl_'):
                applicant_id = applicant_id[5:]

            # Perform the delete request
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    "DELETE",
                    f"{self.base_url}agent-hub/apply/delete-lead",
                    headers=self.request_headers(self.bearer_token_agent),
                    json={'MerchantCode': applicant_id}
                )
                if response.status_code == 204:
                    return {}
                response.raise_for_status()

            return self.add_object_id(response.json()['data'])

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Apply apps delete'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Apply apps delete'}, str(error)))

    async def __add_applicant_document(self, applicant, params):
        if isinstance(applicant, dict):
            applicant_id = applicant.get('object_id', applicant)
        else:
            applicant_id = applicant
        if applicant_id.startswith('appl_'):
            applicant_id = applicant_id[5:]

        data = {
            'MerchantCode': applicant_id,
            'MerchantDocuments': [params]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}agent-hub/apply/add-documents", json=data,
                                             headers=self.request_headers(self.bearer_token_agent))
                response.raise_for_status()
                return self.add_object_id(response.json())
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Apply documents add'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Apply documents add'}, str(error)))

    async def __delete_applicant_document(self, document):
        if isinstance(document, dict):
            document_id = document.get('object_id', document)
        else:
            document_id = document
        try:
            if document_id.startswith('doc_'):
                document_id = document_id[4:]

            async with httpx.AsyncClient() as client:
                response = await client.request(
                    "DELETE",
                    f"{self.base_url}agent-hub/apply/delete-documents",
                    headers=self.request_headers(self.bearer_token_agent),
                    json={'MerchantDocuments': [{'DocumentCode': document_id}]}
                )
                if response.status_code == 204:
                    return {}
                response.raise_for_status()

            return self.add_object_id(response.json())

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Apply document delete'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Apply document delete'}, str(error)))

    async def __submit_applicant_for_signature(self, applicant):
        if isinstance(applicant, dict):
            applicant_id = applicant.get('object_id', applicant)
        else:
            applicant_id = applicant
        try:
            if applicant_id.startswith('appl_'):
                applicant_id = applicant_id[5:]

            # Perform the POST request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}agent-hub/apply/submit-for-signature",
                    json={'MerchantCode': applicant_id},
                    headers=self.request_headers(self.bearer_token_agent)
                )
                response.raise_for_status()

            return self.add_object_id(response.json())

        except httpx.HTTPError as error:
            return self.manage_error({'source': 'API Submit for signature'}, error.response if error.response else {})
        except Exception as error:
            return self.manage_error({'source': 'API Submit for signature'}, str(error))

    async def __sub_agents(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}agent-hub/sub-agents",
                    headers=self.request_headers(self.bearer_token_agent)
                )
                response.raise_for_status()  # Ensure we raise an exception for HTTP errors
                data = response.json()
                sub_agents = [self.add_object_id(sub_agent) for sub_agent in data.get('data', [])]
                return sub_agents
            except httpx.HTTPError as http_error:
                # Handle HTTP errors
                raise Exception(self.manage_error({'source': 'API List sub agents'},
                                                  http_error.response if http_error.response else {}))
            except Exception as error:
                # Handle other potential errors
                raise Exception(self.manage_error({'source': 'API List sub agents'}, str(error)))

    async def __update_applicant(self, obj, new_data):
        if isinstance(obj, dict):
            data_id = obj.get('object_id', obj)
        else:
            data_id = obj

        if data_id.startswith('appl_'):
            data_id = data_id[5:]

        default_data = {
            "bank_account_type": "01",
            "slugId": "financial_information",
            "skipGIACT": True
        }
        new_data = {**default_data, **new_data}  # Merge default_data with new_data

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(f"{self.base_url}agent-hub/apply-apps/{data_id}",
                                              json=new_data,
                                              headers=self.request_headers(self.bearer_token_agent))
                response.raise_for_status()
                if response.status_code == 200:
                    return await self.__retrieve_applicant(data_id)
                return self.add_object_id(response.json())
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API update Application info'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API update Application info'}, str(error)))

    async def __create_plan(self, data):
        data.setdefault('currency', 'usd')
        data.setdefault('plan_type', 'digital')

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}plans", json=data,
                                             headers=self.request_headers(self.bearer_token))
                response.raise_for_status()
                return self.add_object_id(response.json().get('data'))
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Create plan ...'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Create plan ...'}, str(error)))

    async def __list_plans(self, params=None):
        if params is None:
            params = {}
        if 'limit' not in params:
            params['limit'] = "99999"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}plans",
                                            headers=self.request_headers(self.bearer_token), params=params)
                response.raise_for_status()
                data = response.json().get('data', {})
                plans = [self.add_object_id(plan) for plan in data]
                pagination = response.json().get('meta', {}).get('pagination', {})
                pagination.pop('links', None)
                return {'plans': plans, 'pagination': pagination}
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get all plans'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get all plans'}, str(error)))

    async def __get_plan(self, params):
        if isinstance(params, dict):
            data = params.get('object_id', params)
        else:
            data = params
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}plans/{data}",
                                            headers=self.request_headers(self.bearer_token))
                response.raise_for_status()
                data = response.json().get('data', {})
                return self.add_object_id(data)
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get plan details'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get plan details'}, str(error)))

    async def __update_plan(self, params, new_data):
        if isinstance(params, dict):
            data_id = params.get('object_id', params)
        else:
            data_id = params
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}plans/{data_id}",
                    json=new_data,
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
                return self.add_object_id(response.json().get('data', {}))
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API update customer info'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API update customer info'}, str(error)))

    async def __delete_plan(self, params):
        if isinstance(params, dict):
            data_id = params.get('object_id', params)
        else:
            data_id = params
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}plans/{data_id}",
                    headers=self.request_headers(self.bearer_token)
                )
                if response.status_code == 204:
                    return {}
                response.raise_for_status()
                return self.add_object_id(response.json().get('data', {}))
        except httpx.HTTPError as error:
            raise Exception(self.manage_error({'source': 'API delete plan'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API delete plan'}, str(error)))

    async def __create_subscription(self, params, new_data=None):
        if isinstance(params, dict):
            data_id = params.get('object_id', params)
        else:
            data_id = params
        try:
            if not new_data:
                new_data = {}
            new_data['plan_id'] = data_id
            new_data['customer_id'] = (
                new_data['customer_id'][4:] if new_data['customer_id'].startswith('cus_') else new_data['customer_id']
            )
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}subscriptions",
                    json=new_data,
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
                return self.add_object_id(response.json().get('data', {}))
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Create subscription'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Create subscription'}, str(error)))

    async def __list_subscriptions(self, params=None):
        if params is None:
            params = {}
        if 'limit' not in params:
            params['limit'] = "99999"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}subscriptions", params=params,
                                            headers=self.request_headers(self.bearer_token))
                response.raise_for_status()
                data = response.json().get('data', {})
                subscriptions = [self.add_object_id(sub) for sub in data]
                pagination = response.json().get('meta', {}).get('pagination', {})
                pagination.pop('links', None)
                return {'subscriptions': subscriptions, 'pagination': pagination}
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get all subscriptions'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get all subscriptions'}, str(error)))

    async def __update_subscription(self, params, new_data):
        if isinstance(params, dict):
            data_id = params.get('object_id', params)
        else:
            data_id = params
        try:
            if data_id.startswith('sub_'):
                data_id = data_id[4:]
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}subscriptions/{data_id}",
                    json=new_data,
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
                data = response.json().get('data', {})
                return self.add_object_id(data)
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API update customer info'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API update customer info'}, str(error)))

    async def __cancel_subscription(self, params):
        if isinstance(params, dict):
            data_id = params.get('object_id', params)
        else:
            data_id = params
        try:
            if data_id.startswith('sub_'):
                data_id = data_id[4:]
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}subscriptions/{data_id}/cancel",
                    json={},
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
                data = response.json().get('data', {})
                return self.add_object_id(data)
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API cancel subscription'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API cancel subscription'}, str(error)))

    # Split campaigns
    async def __create_campaign(self, data):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}agent-hub/campaigns",
                    json=data,
                    headers=self.request_headers(self.bearer_token_agent)
                )
                response.raise_for_status()  # Raises an exception for HTTP error responses
                return self.add_object_id(response.json()['data'])
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Create campaign ...'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Create campaign ...'}, {'message': str(error)}))

    async def __list_campaigns(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}agent-hub/campaigns",
                    headers=self.request_headers(self.bearer_token_agent),
                    params={'limit': 0}
                )
                response.raise_for_status()  # Raises an exception for HTTP error responses
                return self.add_object_id(response.json()['data'])
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get campaigns status'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get campaigns status'}, {'message': str(error)}))

    async def __get_campaign(self, key):
        try:
            key_id = key.get('object_id', key) if isinstance(key, dict) else key
            if key_id.startswith('cmp_'):
                key_id = key_id[4:]

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}agent-hub/campaigns/{key_id}",
                    headers=self.request_headers(self.bearer_token_agent),
                    params={'limit': 0}
                )
                response.raise_for_status()  # Ensure we handle HTTP errors
                return self.add_object_id(response.json()['data'])

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get campaigns status'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get campaigns status'}, str(error)))

    async def __update_campaign(self, data, new_data):
        data_id = data.get('object_id', data) if isinstance(data, dict) else data
        if data_id.startswith('cmp_'):
            data_id = data_id[4:]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}agent-hub/campaigns/{data_id}",
                    json=new_data,
                    headers=self.request_headers(self.bearer_token_agent)
                )
                response.raise_for_status()
                return self.add_object_id(response.json()['data'])

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API update customer info'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API update customer info'}, str(error)))

    async def __list_campaign_accounts(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}account/my-accounts",
                    headers=self.request_headers(self.bearer_token_agent)
                )
                response.raise_for_status()
                data = response.json()
                proc_merchants = [self.add_object_id(p_m) for p_m in data]
                if isinstance(data, dict):
                    pagination = data.get('meta', {}).get('pagination', {})
                    pagination.pop('links', None)
                else:
                    pagination = {}
                return {'campaign_accounts': proc_merchants, 'pagination': pagination}
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get all merchants'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get all merchants'}, str(error)))

    async def __list_agent_charges(self, params=None):
        def format_date(date):
            return date.strftime('%Y-%m-%d')

        try:
            from_date = params.get('from_date') if params else None
            to_date = params.get('to_date') if params else None

            if not from_date or not to_date:
                current_date = datetime.now()
                from_date = format_date(current_date - timedelta(days=30))
                to_date = format_date(current_date + timedelta(days=1))
                params = {
                    'from_date': from_date,
                    'to_date': to_date
                }
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}alt/agent/charges"
                response = await client.get(
                    url,
                    headers=self.request_headers(self.bearer_token_agent),
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                charges = [self.add_object_id(charge) for charge in data['data']]
                if isinstance(data, dict):
                    pagination = data.get('meta', {}).get('pagination', {})
                    pagination.pop('links', None)
                else:
                    pagination = {}
                return {'charges': charges, 'pagination': pagination}

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get all agent charges'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get all agent charges'}, str(error)))

    async def __list_agent_deposits(self, params: Optional[Dict[str, Any]]):

        try:
            from_date = params.get("from_date") if params else None
            to_date = params.get("to_date") if params else None
            account_ids = params.get("account_ids", []) if params else []
            mids = params.get("mids", []) if params else []

            if not from_date or not to_date:
                current_date = datetime.now()
                year, month = current_date.year, current_date.month
                from_date = f"{year}-{month:02d}-01"
                last_day = monthrange(year, month)[1]
                to_date = f"{year}-{month:02d}-{last_day:02d}"

            try:
                from_dt = datetime.strptime(from_date, "%Y-%m-%d")
                to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            except (TypeError, ValueError):
                raise ValueError("from_date and to_date must be in format Y-m-d")
            if to_dt < from_dt:
                raise ValueError("to_date must be after or equal to from_date")

            if not isinstance(account_ids, list):
                account_ids = [account_ids]
            account_ids = [str(x) for x in account_ids]
            if not isinstance(mids, list):
                mids = [mids]
            mids = [str(x) for x in mids]

            params = [
                         ("from_date", "2023-11-01"),
                         ("to_date", "2023-11-04"),
                     ] + [("mids[]", mid) for mid in mids] + [("account_ids[]", acc) for acc in account_ids]

            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}agent/deposit/summary"
                response = await client.get(
                    url,
                    headers=self.request_headers(self.bearer_token_agent),
                    params=params,  # ✅ multiple mids/account_ids handled correctly
                )
                response.raise_for_status()
                data = response.json()

                deposits = [self.add_object_id(deposit) for deposit in data["data"]]

                pagination = {}
                if isinstance(data, dict):
                    pagination = data.get("meta", {}).get("pagination", {})
                    pagination.pop("links", None)

                return {"deposits": deposits, "pagination": pagination}

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error(
                    {"source": "API get all agent deposits"},
                    error.response if error.response else {},
                )
            )
        except Exception as error:
            raise Exception(
                self.manage_error({"source": "API get all agent deposits"}, str(error))
            )

    async def __list_cases(self, params=None):
        def format_date(date):
            return date.strftime('%Y-%m-%d')  # Format date to 'YYYY-MM-DD'

        try:
            if params is None:
                current_date = datetime.now()
                tomorrow_date = format_date(current_date + timedelta(days=1))
                last_month_date = format_date(current_date - timedelta(days=30))
                params = {
                    'report_date[gte]': last_month_date,
                    'report_date[lte]': tomorrow_date
                }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}cases",
                    headers=self.request_headers(self.bearer_token),
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                cases = [self.add_object_id(case) for case in data['data']]
                if isinstance(data, dict):
                    pagination = data.get('meta', {}).get('pagination', {})
                    pagination.pop('links', None)
                else:
                    pagination = {}
                return {'cases': cases, 'pagination': pagination}

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get all disputes'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get all disputes'}, str(error)))

    async def __get_case(self, params):
        data_id = params.get('object_id', params) if isinstance(params, dict) else params
        data_id = data_id[4:] if data_id.startswith('dis_') else data_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}cases/{data_id}",
                    headers=self.request_headers(self.bearer_token)
                )
                response.raise_for_status()
                # Return the transformed data
                return self.add_object_id(response.json().get('primary_case', {}).get('data', {}))

        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API get dispute details'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API get dispute details'}, str(error)))

    async def __add_document_case(self, dispute, params):
        dispute_id = dispute.get('object_id', dispute) if isinstance(dispute, dict) else dispute
        if dispute_id.startswith('dis_'):
            dispute_id = dispute_id[4:]

        headers = {}
        form_data = ""
        form_data_buffer = None
        if params and params.get('DocumentDataBase64'):
            binary_file = base64.b64decode(params['DocumentDataBase64'])
            boundary = '----WebKitFormBoundary' + '3OdUODzy6DLxDNt8'  # Create a unique boundary

            form_data += f"--{boundary}\r\n"
            form_data += f"Content-Disposition: form-data; name=\"file\"; filename=\"filename1.png\"\r\n"
            form_data += f"Content-Type: {params.get('mimeType', 'application/pdf')}\r\n\r\n"
            form_data += binary_file.decode('latin1')
            form_data += f"\r\n--{boundary}--\r\n"

            if params.get('text'):
                form_data += f"--{boundary}\r\n"
                form_data += f"Content-Disposition: form-data; name=\"text\"\r\n\r\n"
                form_data += f"{params['text']}\r\n"
                form_data += f"--{boundary}--\r\n"

            form_data_buffer = form_data.encode('latin1')

            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(form_data_buffer))
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}cases/{dispute_id}/evidence",
                    content=form_data_buffer,
                    headers=self.request_headers(self.bearer_token, **headers)
                )
                response.raise_for_status()

                sub_response = await client.post(
                    f"{self.base_url}cases/{dispute_id}/submit",
                    json={'message': params.get('message', 'Case number#: xxxxxxxx, submitted by SDK')},
                    headers=self.request_headers(self.bearer_token)
                )
                sub_response.raise_for_status()

                return self.add_object_id(response.json())
        except httpx.HTTPError as error:
            raise Exception(
                self.manage_error({'source': 'API Dispute documents add'}, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error({'source': 'API Dispute documents add'}, str(error)))

    async def __login(self):
        seed = {'source': 'Payarc Connect Login'}
        try:
            async with httpx.AsyncClient() as client:
                request_body = {
                    "SecretKey": self.bearer_token
                }
                response = await client.post(
                    f"{self.payarc_connect_base_url}/Login",
                    json=request_body
                )
                response.raise_for_status()

                data = response.json()

                try:
                    bearer_token_info = data.get('BearerTokenInfo', None)
                    access_token = bearer_token_info.get('AccessToken', None)
                    self.payarc_connect_access_token = access_token
                except Exception as error:
                    errorMessage = data.get('ErrorMessage', None)
                    errorCode = data.get('ErrorCode', None)
                    raise PayarcConnectException(errorMessage, errorCode)
                return data
        except PayarcConnectException as error:
            raise Exception(self.manage_payarc_connect_error(seed, error))
        except httpx.HTTPError as error:
            raise Exception(self.manage_error(seed, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error(seed, str(error)))

    async def __sale(self, tenderType, ecrRefNum, amount, deviceSerialNo):
        seed = {'source': 'Payarc Connect Sale'}
        request_body = {
            "TenderType": tenderType,
            "TransType": "SALE",
            "ECRRefNum": ecrRefNum,
            "Amount": amount,
            "DeviceSerialNo": deviceSerialNo
        }
        return await self.payarc_connect_transaction(seed, request_body)

    async def __void(self, payarcTransactionId, deviceSerialNo):
        seed = {'source': 'Payarc Connect Void'}
        request_body = {
            "TransType": "VOID",
            "PayarcTransactionId": payarcTransactionId,
            "DeviceSerialNo": deviceSerialNo
        }
        return await self.payarc_connect_transaction(seed, request_body)

    async def __refund(self, amount, payarcTransactionId, deviceSerialNo):
        seed = {'source': 'Payarc Connect Refund'}
        request_body = {
            "TransType": "REFUND",
            "Amount": amount,
            "PayarcTransactionId": payarcTransactionId,
            "DeviceSerialNo": deviceSerialNo
        }
        return await self.payarc_connect_transaction(seed, request_body)

    async def __blind_credit(self, ecrRefNum, amount, token, expDate, deviceSerialNo):
        seed = {'source': 'Payarc Connect Blind Credit'}
        request_body = {
            "TransType": "RETURN",
            "ECRRefNum": ecrRefNum,
            "Amount": amount,
            "Token": token,
            "ExpDate": expDate,
            "DeviceSerialNo": deviceSerialNo
        }
        return await self.payarc_connect_transaction(seed, request_body)

    async def __auth(self, ecrRefNum, amount, deviceSerialNo):
        seed = {'source': 'Payarc Connect Auth'}
        request_body = {
            "TransType": "AUTH",
            "ECRRefNum": ecrRefNum,
            "Amount": amount,
            "DeviceSerialNo": deviceSerialNo
        }
        return await self.payarc_connect_transaction(seed, request_body)

    async def __post_auth(self, ecrRefNum, origRefNum, amount, deviceSerialNo):
        seed = {'source': 'Payarc Connect Post Auth'}
        request_body = {
            "TransType": "POSTAUTH",
            "ECRRefNum": ecrRefNum,
            "OrigRefNum": origRefNum,
            "Amount": amount,
            "DeviceSerialNo": deviceSerialNo
        }
        return await self.payarc_connect_transaction(seed, request_body)

    async def __last_transaction(self, deviceSerialNo):
        seed = {'source': 'Payarc Connect Last Transaction'}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.payarc_connect_base_url}/LastTransaction",
                    headers=self.request_headers(self.payarc_connect_access_token),
                    params={
                        "DeviceSerialNo": deviceSerialNo
                    }
                )
                response.raise_for_status()
                data = response.json()
                errorCode = data.get('ErrorCode', None)
                if errorCode == 0:
                    return data
                else:
                    raise PayarcConnectException(data.get('ErrorMessage', None), errorCode)
        except PayarcConnectException as error:
            raise Exception(self.manage_payarc_connect_error(seed, error))
        except httpx.HTTPError as error:
            raise Exception(self.manage_error(seed, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error(seed, str(error)))

    async def __server_info(self):
        seed = {'source': 'Payarc Connect Server Info'}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.payarc_connect_base_url}/ServerInfo",
                                            headers=self.request_headers(self.payarc_connect_access_token))
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as error:
            raise Exception(self.manage_error(seed, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error(seed, str(error)))

    async def __terminals(self):
        seed = {'source': 'Payarc Connect Terminals'}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.payarc_connect_base_url}/Terminals",
                                            headers=self.request_headers(self.payarc_connect_access_token))
                response.raise_for_status()
                data = response.json()
                errorCode = data.get('ErrorCode', None)
                if errorCode == 0:
                    return data
                else:
                    raise PayarcConnectException(data.get('ErrorMessage', None), errorCode)
        except PayarcConnectException as error:
            raise Exception(self.manage_payarc_connect_error(seed, error))
        except httpx.HTTPError as error:
            raise Exception(self.manage_error(seed, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error(seed, str(error)))

    def add_object_id(self, obj):
        def handle_object(obj):
            if 'id' in obj or 'customer_id' in obj:
                if obj.get('object') == 'Charge':
                    obj['object_id'] = f"ch_{obj['id']}"
                    obj['create_refund'] = partial(self.__refund_charge, obj)
                elif obj.get('object') == 'customer':
                    obj['object_id'] = f"cus_{obj['customer_id']}"
                    obj['update'] = partial(self.__update_customer, obj)
                    obj['cards'] = {}
                    obj['cards']['create'] = partial(self.__add_card_to_customer, obj)
                    if 'bank_accounts' not in obj:
                        obj['bank_accounts'] = {}
                    obj['bank_accounts']['create'] = partial(self.__add_bank_acc_to_customer, obj)
                    if 'charges' not in obj:
                        obj['charges'] = {}
                    obj['charges']['create'] = partial(self.__create_charge, obj)
                elif obj.get('object') == 'Token':
                    obj['object_id'] = f"tok_{obj['id']}"
                elif obj.get('object') == 'Card':
                    obj['object_id'] = f"card_{obj['id']}"
                elif obj.get('object') == 'BankAccount':
                    obj['object_id'] = f"bnk_{obj['id']}"
                elif obj.get('object') == 'ACHCharge':
                    obj['object_id'] = f"ach_{obj['id']}"
                    obj['create_refund'] = partial(self.__refund_charge, obj)
                elif obj.get('object') == 'ApplyApp':
                    obj['object_id'] = f"appl_{obj['id']}"
                    obj['retrieve'] = partial(self.__retrieve_applicant, obj)
                    obj['delete'] = partial(self.__delete_applicant, obj)
                    obj['add_document'] = partial(self.__add_applicant_document, obj)
                    obj['submit'] = partial(self.__submit_applicant_for_signature, obj)
                    obj['update'] = partial(self.__update_applicant, obj)
                    obj['list_sub_agents'] = partial(self.__sub_agents, obj)
                elif obj.get('object') == 'ApplyDocuments':
                    obj['object_id'] = f"doc_{obj['id']}"
                    obj['delete'] = partial(self.__delete_applicant_document, obj)
                elif obj.get('object') == 'Campaign':
                    obj['object_id'] = f"cmp_{obj['id']}"
                    obj['update'] = partial(self.__update_campaign, obj)
                    obj['retrieve'] = partial(self.__get_campaign, obj)
                elif obj.get('object') == 'User':
                    obj['object_id'] = f"usr_{obj['id']}"
                elif obj.get('object') == 'Subscription':
                    obj['object_id'] = f"sub_{obj['id']}"
                    obj['cancel'] = partial(self.__cancel_subscription, obj)
                    obj['update'] = partial(self.__update_subscription, obj)
                elif obj.get('object') == 'Cases':
                    obj['object'] = 'Dispute'
                    obj['object_id'] = f"dis_{obj['id']}"
                elif obj.get('object') == 'Account':
                    obj['object'] = 'Merchant'
                    obj['object_id'] = f"acc_{obj['id']}"
            elif 'MerchantCode' in obj:
                obj['object_id'] = f"appl_{obj['MerchantCode']}"
                obj['object'] = 'ApplyApp'
                del obj['MerchantCode']
                obj['retrieve'] = partial(self.__retrieve_applicant, obj)
                obj['delete'] = partial(self.__delete_applicant, obj)
                obj['add_document'] = partial(self.__add_applicant_document, obj)
                obj['submit'] = partial(self.__submit_applicant_for_signature, obj)
                obj['update'] = partial(self.__update_applicant, obj)
                obj['list_sub_agents'] = partial(self.__sub_agents, obj)
            elif 'plan_id' in obj:
                obj['object_id'] = obj['plan_id']
                obj['object'] = 'Plan'
                del obj['plan_id']
                obj['retrieve'] = partial(self.__get_plan, obj)
                obj['update'] = partial(self.__update_plan, obj)
                obj['delete'] = partial(self.__delete_plan, obj)
                obj['create_subscription'] = partial(self.__create_subscription, obj)

            for key in obj:
                if isinstance(obj[key], dict):
                    handle_object(obj[key])
                elif isinstance(obj[key], list):
                    for item in obj[key]:
                        if isinstance(item, dict):
                            handle_object(item)

        handle_object(obj)
        return obj

    def manage_error(self, seed=None, error=None):
        seed = seed or {}

        # Determine the error_json
        error_code = None
        if hasattr(error, 'json'):
            try:
                error_json = error.json()
            except ValueError:
                error_json = {}
        elif isinstance(error, dict):
            error_json = error
            error_code = error.get('status_code', 'unKnown')
        else:
            error_json = {}

        # Update seed with error details
        seed.update({
            'object': f"Error {self.version}",
            'type': 'TODO put here error type',
            'errorMessage': error_json.get('message', error) if isinstance(error, str) else error_json.get('message',
                                                                                                           'unKnown'),
            'errorCode': error_code if error_code is not None else getattr(error, 'status_code', 'unKnown'),
            'errorList': error_json.get('errors', 'unKnown'),
            'errorException': error_json.get('exception', 'unKnown'),
            'errorDataMessage': error_json.get('data', {}).get('message', 'unKnown')
        })

        return seed

    async def payarc_connect_transaction(self, seed, request_body):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.payarc_connect_base_url}/Transactions",
                    json=request_body,
                    headers=self.request_headers(self.payarc_connect_access_token)
                )
                response.raise_for_status()
                data = response.json()
                errorCode = data.get('ErrorCode', None)

                if errorCode == 0:
                    return data
                else:
                    raise PayarcConnectException(data.get('ErrorMessage', None), errorCode)

        except PayarcConnectException as error:
            raise Exception(self.manage_payarc_connect_error(seed, error))
        except httpx.HTTPError as error:
            raise Exception(self.manage_error(seed, error.response if error.response else {}))
        except Exception as error:
            raise Exception(self.manage_error(seed, str(error)))

    def manage_payarc_connect_error(self, seed, error):
        error_dict = {
            'message': str(error),
            'status_code': error.error_code
        }
        return self.manage_error(seed, error_dict)
