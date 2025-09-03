import unittest

from ..kawa_base_e2e_test import KawaBaseTest
from datetime import date
import pandas as pd
import uuid


class TestComputationDsl(KawaBaseTest):

    @unittest.skip("requires non trivial migration work on BE")
    def test_that_a_gen_ai_view_is_generated_properly(self):
        # setup
        state_data = pd.DataFrame([
            {'id': 1, 'state': 'California', 'profit': 1, 'date': date(2022, 1, 1)},
            {'id': 2, 'state': 'Ohio', 'profit': 2, 'date': date(2022, 2, 1)},
            {'id': 3, 'state': 'New Jersey', 'profit': 3, 'date': date(2022, 3, 1)},
            {'id': 4, 'state': 'New York', 'profit': 4, 'date': date(2022, 4, 1)},
            {'id': 5, 'state': 'New York', 'profit': 5, 'date': date(2022, 4, 4)},
            {'id': 6, 'state': 'New York', 'profit': 10, 'date': date(2023, 4, 1)},
        ])

        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=state_data, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        sheet = self.kawa.entities.sheets().get_entity(entity_id_or_name=unique_id)
        sheet_id = sheet.get('id')
        cmd = self.kawa.commands
        ai_view = cmd.run_command(
            command_name='createLayout',
            command_parameters={
                'layoutType': 'GENERATIVE_AI',
                'sheetId': str(sheet_id),
                'status': 'ACTIVE',
                'createLayoutWithoutFields': False
            })

        ai_view_id = ai_view.get('id')
        associated_conversation_id = ai_view.get('associatedConversationId')
        chat = self.kawa.chat(
            copilot_type='generative-view-copilot',
            conversation_id=associated_conversation_id)

        message = chat.append_message(
            layout_id=ai_view_id,
            message='Profit per state in 2022'
        )
        response = chat.get_answer_to_message(message_id=message.get('id'))
        generated_content = response.get('content')[0].get('value')
        cmd.run_command(
            command_name='ReplaceGeneratedContent',
            command_parameters={
                'layoutId': ai_view_id,
                'generatedEchartContent': {
                    'echartConfig': generated_content.get('echartConfig'),
                    'dataMappingFunction': generated_content.get('dataMappingFunction'),
                    'sqlRequest': generated_content.get('sql'),
                    'generatedFields': generated_content.get('fields'),
                }
            }
        )

        # when
        df = self.kawa.sheet().view_id(ai_view_id).compute()

        # then
        self.assertListEqual(sorted(list(df.iloc[:, 0])), sorted(['California', 'Ohio', 'New Jersey', 'New York']))
        self.assertListEqual(sorted(list(df.iloc[:, 1])), sorted([1, 2, 3, 4 + 5]))
