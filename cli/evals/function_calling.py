import openai
import json
from ..cost import input, output

class functionCalling:
    def __init__(self, test_cases, number_of_prompts, model_test, model_test_temperature, model_test_max_tokens, model_generation, model_generation_temperature, prompts, functions, function_call, best_prompts):

        self.test_cases = test_cases
        self.number_of_prompts = number_of_prompts
        self.model_test = model_test
        self.model_generation = model_generation
        self.model_test_temperature = model_test_temperature
        self.model_test_max_tokens = model_test_max_tokens
        self.model_generation_temperature = model_generation_temperature
        self.prompts = prompts
        self.best_prompts = best_prompts
        self.functions = functions
        self.function_call = function_call
        self.system_gen_system_prompt = """Your job is to generate system prompts for GPT, given a description of the use-case and some test cases.

In your generated prompt, you should describe how the AI should behave in plain English. Include what it will see, and what it's allowed to output. Be creative with prompts to get the best possible results. The AI knows it's an AI -- you don't need to tell it this.

You should respond a function_call and nothing else. Don't text us back.

You will be graded based on the performance of your prompt... but don't cheat! You cannot include specifics about the test cases in your prompt. Any prompts with examples will be disqualified.

Most importantly, output NOTHING but the prompt. Do not include anything else in your message."""

    def test_candidate_prompts(self):
        cost = 0
        tokens_input = 0
        tokens_output = 0
        prompt_results = {prompt: {'correct': 0, 'total': 0} for prompt in self.prompts}
        results = [{"method": "Function_calling"}]
        for prompt in self.prompts:
            prompt_and_results = [{"prompt": prompt}]
            for test_case in self.test_cases:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"{test_case['inout']}"}
                    ],
                    functions=self.functions,
                    function_call=self.function_call,
                    max_tokens=self.model_test_max_tokens,
                    temperature=self.model_test_temperature,
                )
                if "function_call" in response['choices'][0]['message']:
                # Update model results
                    json_object = json.loads(str(response['choices'][0]['message']['function_call']['arguments']))
                    if test_case['output1'] == response.choices[0].message.function_call.name and json_object['file_type'] == test_case['output2']:
                        prompt_results[prompt]['correct'] += 1
                    prompt_results[prompt]['total'] += 1
                    if test_case['output1'] == response.choices[0].message.function_call.name and test_case['output2'] == json_object['file_type']:
                        a = True
                    if test_case['output1'] == response.choices[0].message.function_call.name and not (test_case['output2'] == json_object['file_type']):
                        a = 'variable error'
                    if not (test_case['output1'] == response.choices[0].message.function_call.name) and test_case['output2'] == json_object['file_type']:
                        a = 'function error'
                    if not (test_case['output1'] == response.choices[0].message.function_call.name) and (not test_case['output2'] == json_object['file_type']):
                        a = 'function and variable error'
                    prompt_and_results.append({"test": test_case['inout'], "answer": {"function": f"{response.choices[0].message.function_call.name}", "variable": f"{json_object['file_type']}"}, "ideal": {"function": f"{test_case['output1']}", "variable": f"{test_case['output2']}"}, "result": a})
                partial_tokens_input = response["usage"]["prompt_tokens"]
                partial_tokens_output = response["usage"]["completion_tokens"]
                tokens_input = tokens_input + partial_tokens_input
                tokens_output = tokens_output + partial_tokens_output
                if "function_call" not in response['choices'][0]['message']:
                    prompt_and_results.append({"test": test_case['inout'], "answer": 'not a function call', "ideal": f"{test_case['output1']}" + " " f"{test_case['output2']}", "result": 'Received text data instead of JSON.'})
                    prompt_results[prompt]['total'] += 1
            results.append(prompt_and_results)
            prompt_and_results = []
        cost_input = input.cost(tokens_input, self.model_test)
        cost_output = output.cost(tokens_output, self.model_test)
        cost = cost + cost_input + cost_output

        # Calculate and print the percentage of correct answers and average time for each model
        best_prompt = self.prompts[0]
        best_percentage = 0
        data_list = []
        for i, prompt in enumerate(self.prompts):
            correct = prompt_results[prompt]['correct']
            total = prompt_results[prompt]['total']
            percentage = (correct / total) * 100
            data_list.append({"prompt": prompt, "rating": percentage})
            print(f"Prompt {i+1} got {percentage:.2f}% correct.")
            if percentage >= best_percentage:
                best_percentage = percentage
                best_prompt = prompt
        sorted_data = sorted(data_list, key=lambda x: x['rating'], reverse=True)
        best_prompts = sorted_data[:self.best_prompts]
        print(f"The best prompt was '{best_prompt}' with a correctness of {best_percentage:.2f}%.")
        sorted_data.append(results)
        return sorted_data, best_prompts, cost, tokens_input, tokens_output
    
    def evaluate_optimal_prompt(self):
        return self.test_candidate_prompts()