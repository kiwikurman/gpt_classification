import unittest
from unittest.mock import patch, Mock
import main


class TestGptLineClassifier(unittest.TestCase):

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='l,i,n,e1\n   line2\nline3\n\n')
    def test_read_lines(self, mock_open):
        lines = main.read_lines()
        self.assertEqual(lines, ['line1', 'line2', 'line3'])

    @patch('main.openai.ChatCompletion.create')
    def test_classify_batch(self, mock_api_call):
        mock_api_call.return_value = {'choices': [{'message': {'content': 'mocked_content'}}]}
        batch = ['line1', 'line2']
        result = main.classify_batch(batch, 0, 2)
        self.assertEqual(result, 'mocked_content')

    @patch('main.openai.ChatCompletion.create')
    def test_classify_batch_api_input_params(self, mock_api_call):
        mock_api_call.return_value = {'choices': [{'message': {'content': 'mocked_content'}}]}
        batch = ['line1', 'line2']
        result = main.classify_batch(batch, 0, 2)
        expected_message = [
            {"role": "system",
             "content": "for each line in the following text, i need exactly one line output with the following comma-separated format: summary in english of the input, classification label."},
            {"role": "system",
             "content": "the label should be one of the following: mechanical, electrical, clean up, operational, temperature. the operational label should capture anything related to a device malfunctioning. the temperature label should capture anything regarding temperature change."},
            {"role": "system", "content": "the summary must be in english."},
            {"role": "system",
             "content": "an example for an output is: Handle does not close properly indicating that the oven is not closed, mechanical"},
            {"role": "user", "content": "line1\nline2"}]
        mock_api_call.assert_called_once_with(model="gpt-3.5-turbo", messages=expected_message, temperature=0)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_write_to_file(self, mock_open):
        main.write_to_file(['line1', 'line2'])
        mock_open().write.assert_called_with('line1\nline2')

    @patch('main.classify_batch')
    def test_process_lines_retries(self, mock_classify_batch):
        mock_classify_batch.side_effect = [TimeoutError, TimeoutError, "mock_result"]
        lines = ["line1", "line2", "line3", "line4", "line5"]
        result = main.process_lines(lines, batch_size=5)
        self.assertEqual(mock_classify_batch.call_count, 3)
        self.assertEqual(result, ["mock_result", ])

    @patch('main.classify_batch')
    def test_process_lines_basic(self, mock_classify_batch):
        # Mock classify_batch to return a fixed structure
        mock_classify_batch.return_value = "summary, label"

        # Sample lines to process
        lines = [f"line{i}" for i in range(1, 11)]  # 10 lines

        # Call the function to test
        result = main.process_lines(lines, batch_size=2)
        # Check if the result has the correct structure
        self.assertEqual(len(result), 5)  # 10 lines with batch size of 2 should result in 5 batches
        for batch_result in result:
            self.assertEqual(batch_result, "summary, label")  # Each batch should return "summary, label"


if __name__ == '__main__':
    unittest.main()
