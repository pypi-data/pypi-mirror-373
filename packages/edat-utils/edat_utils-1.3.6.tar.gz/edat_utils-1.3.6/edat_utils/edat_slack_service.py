import logging
import requests

logger = logging.getLogger(__name__)


class EdatSlackService:
    """ Serviço para integração com o Slack API """

    def enviar_mensagem(
            self,
            slack_url: str,
            id_chat: str,
            nome_chat: str,
            sistema: str,
            descricao: str,
            prioridade: str = None,
            link: str = None,
            icon_emoji: str = None,
    ) -> bool:
        """ Envia mensagem em canal específico do Slack

            :param slack_url: URL para conexão com o Slack API (específico para cada sistema/canal do slack)
            :param id_chat: Identificador do chat definido no slack
            :param nome_chat: Nome do chat definido no slack
            :param sistema: Sistema referente a mensagem a ser enviada
            :param descricao: Descrição da mensagem a ser enviada
            :param prioridade: Prioridade da mensagem a ser enviada (Alta, Baixa, etc)
            :param link: Link qualquer, por exemplo para acesso a determinado log referente a mensagem
            :param icon_emoji: emoji referente a mensagem (por exemplo: :telephone:, :lady_beetle:, etc)
        """

        if not all([slack_url, id_chat, nome_chat, sistema, descricao]):
            logger.info(
                msg=f'Estão faltando parâmetros necessários para o envio da mensagem '
                    f'['
                    f'slack_url={slack_url}, '
                    f'id_chat={id_chat}, '
                    f'nome_chat={nome_chat}, '
                    f'sistema={sistema}, '
                    f'descricao={descricao}'
                    f'], '
                    f'mensagem não enviada.'
            )
            return False

        msg_texto = descricao.replace('"', "'")

        try:
            logger.info(msg=f'msg_texto={msg_texto}')

            # Construção da mensagem de forma condicional
            mensagem = f"[{sistema}"
            if prioridade:
                mensagem += f" - *{prioridade}*"
            mensagem += "]"
            if link:
                mensagem += f"\n*Link* <{link}>"
            mensagem += f"\n\n{msg_texto}"

            # Construção do payload
            dados = {
                'payload': (
                    f'{{'
                    f'"channel": "{id_chat}", '
                    f'"username": "{nome_chat}", '
                    f'"text": "{mensagem}", '
                    f'"icon_emoji": "{icon_emoji if icon_emoji else ":telephone:"}"'
                    f'}}'
                )
            }
            logger.info(msg=f'dados={dados}')
            response = requests.post(slack_url, data=dados)
            if response.status_code == 200:
                logger.info(
                    msg=f'Mensagem enviada para o slack '
                        f'['
                        f'id_chat={id_chat}, '
                        f'nome_chat={nome_chat}, '
                        f'sistema={sistema}, '
                        f'descricao={descricao}'
                        f']'
                )
                return True
            else:
                logger.error(
                    msg=f'Não foi possível enviar mensagem para o slack!\n|Response:{response.text}|\n'
                )
                return False

        except Exception as e:
            logger.error(
                msg=f'Erro ao encaminhar mensagem para o canal do slack! mensagem={msg_texto} erro={e}'
            )
            return False
