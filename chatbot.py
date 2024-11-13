import re
import html2text
from bs4 import BeautifulSoup
from django.db import models
from django.conf import settings
from nltk.stem import WordNetLemmatizer

def get_response(self, user_input):
        split_message = self.preprocess_message(user_input)
        conversation = self.conversation

        try:
            if not self.conversation.user_choice and user_input in ["1", "2", "3", "4", "5", "6", "7"]:
                self.conversation.user_choice = {
                    "1": "equipamentos",
                    "2": "documentos",
                    "3": "NGN L2L",
                    "4": "Diagramas",
                    "5": "Scripts",
                    "6": "MBGP",
                    "7": "IPSLA"
                }.get(user_input, "outros")
                self.conversation.save()

                if self.conversation.user_choice == "documentos":
                    first_entry = True
                    response = self.get_response_documents(user_input, first_entry)
                elif self.conversation.user_choice == "equipamentos":
                    response = self.get_response_equipments(user_input)
                elif self.conversation.user_choice == "NGN L2L":
                    first_entry_NGN = True
                    response = self.get_response_NGN_L2L(user_input, first_entry_NGN)
                elif self.conversation.user_choice == "Diagramas":
                    response = self.get_response_diagram(user_input)
                elif self.conversation.user_choice == "Scripts":
                    response = self.get_response_scripts(user_input)
                elif self.conversation.user_choice == "MBGP":
                    response = self.get_response_MBGP(user_input)
                elif self.conversation.user_choice == "IPSLA":
                    response = self.get_response_IPSLA(user_input)
            else:
                responses = responses_list
                if self.conversation.user_choice == "equipamentos":
                    responses = equipments_list
                elif self.conversation.user_choice == "documentos":
                    responses = documents_list
                elif self.conversation.user_choice == "NGN L2L":
                    responses = NGN_list
                elif self.conversation.user_choice == "Diagramas":
                    responses = diagram_list
                elif self.conversation.user_choice == "Scripts":
                    responses = scripts_list

                if responses == documents_list:
                    first_entry = False
                    response = self.get_response_documents(user_input, first_entry)
                elif self.conversation.user_choice == "NGN L2L":
                    first_entry_NGN = False
                    response = self.get_response_NGN_L2L(user_input, first_entry_NGN)
                elif self.conversation.user_choice == "Diagramas":
                    response = self.get_response_diagram(user_input)
                elif self.conversation.user_choice == "Scripts":
                    response = self.get_response_scripts(user_input)
                elif self.conversation.user_choice == "equipamentos":
                    response = self.get_response_equipments(user_input)
                elif self.conversation.user_choice == "MBGP":
                    response = self.get_response_MBGP(user_input)
                elif self.conversation.user_choice == "IPSLA":
                    response = self.get_response_IPSLA(user_input)
                else:
                    response = self.check_all_messages(split_message, responses)

        except UnboundLocalError:
            # Define uma resposta padrão em caso de erro
            response = "Ocorreu um erro ao processar sua solicitação."

        return response

    def preprocess_message(self, message):
        lemmatizer = WordNetLemmatizer()
        split_message = re.split(r'\s+|[,;?!.-]\s*', message.lower())
        return [lemmatizer.lemmatize(word) for word in split_message]

    def check_all_messages(self, message, responses):
        highest_prob_list = {}

        def message_probability(user_message, recognised_words, single_response=False, required_words=[]):
            message_certainty = 0
            has_required_words = True
            recognised_words_set = set(recognised_words)

            for word in user_message:
                if word in recognised_words_set:
                    message_certainty += 1

            percentage = float(message_certainty) / float(len(recognised_words))

            for word in required_words:
                if word not in user_message:
                    has_required_words = False
                    break

            if has_required_words or single_response:
                return int(percentage * 100)
            else:
                return 0

        def response(bot_response, list_of_words, single_response=False, required_words=[]):
            nonlocal highest_prob_list
            highest_prob_list[bot_response] = message_probability(message, list_of_words, single_response, required_words)

        for res in responses:
            response(
                res["response"],
                res["recognised_words"],
                single_response=res.get("single_response", False),
                required_words=res.get("required_words", [])
            )

        best_match = max(highest_prob_list, key=highest_prob_list.get)
        return "Desculpe, não tenho uma resposta específica para essa pergunta." if highest_prob_list[best_match] < 1 else best_match