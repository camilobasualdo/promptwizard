from marshmallow import Schema, fields, ValidationError, validates

class ModelSchema(Schema):
        name = fields.Str(required=True)
        temperature = fields.Float(required=True)
        max_tokens = fields.Integer(required=True, strict=True)
        @validates('name')
        def validate_name(self, model):
            allowed_names = ['gpt-3.5-turbo', 'gpt-4']
            if model not in allowed_names:
                raise ValidationError(f"'name' must be one of the following: {', '.join(allowed_names)}")
        @validates("temperature")
        def validate_temperature_range(self, value):
            if not (0 <= value <= 2):
                raise ValidationError("'Temperature' must be a float between 0 and 2.")
        @validates("max_tokens")
        def validate_max_tokens(self, value):
            if not (1 <= value):
                raise ValidationError("'max_tokens' must be an integer greater than 0.")

class FirstFormatTestCaseSchema(Schema):
    cases = fields.List(fields.Str(required=True))
    method = fields.Str(required=True)
    model = fields.Nested(ModelSchema)
    description = fields.Str(required=True)

class SecondFormatTestCaseSchema(Schema):
        cases = fields.List(fields.List(fields.Str(required=True)))
        method = fields.Str(required=True)
        model = fields.Nested(ModelSchema)
        description = fields.Str(required=True)
        @validates("cases")
        def validate_cases_list(self, cases):
            for case in cases:
                if len(case) != 2:
                    raise ValidationError("Each test case must consist of 2 strings, the first one being the specific test case and the second one must be the correct answer.")
        @validates("method")
        def validate_method(self, value):
            expected_method1 = "classification.Classification"
            expected_method2 = "equal.Equal"
            expected_method3 = "includes.Includes"
            if value != expected_method1 and value != expected_method2 and value != expected_method3:
                raise ValidationError(f"Method must be '{expected_method1}', '{expected_method2}' or '{expected_method3}'.")

class ThirdFormatFunctionSchema(Schema):
        name = fields.Str(required=True)
        description = fields.Str(required=True)
        parameters = fields.Dict(required=True)

class ThirdFormatTestCaseSchema(Schema):
        cases = fields.List(fields.List(fields.Str(required=True)))
        method = fields.Str(required=True)
        model = fields.Nested(ModelSchema)
        functions = fields.List(fields.Nested(ThirdFormatFunctionSchema))
        function_call = fields.Str(required=True)
        description = fields.Str(required=True)
        @validates("cases")
        def validate_cases_list(self, cases):
            for case in cases:
                if len(case) != 3:
                    raise ValidationError("Each test case must consist of 3 strings, the first one being the specific test case, the second one the correct function to use, and the third one the correct variable.")
        @validates("method")
        def validate_method(self, value):
            expected_method = "function_calling.functionCalling"
            if value != expected_method:
                raise ValidationError(f"Method must be '{expected_method}'.")


class PromptSchema(Schema):
        content = fields.List(fields.Str(required=True))
        number = fields.Integer(required=True)
        change = fields.Str(required=True)
        features = fields.Str(required=True)
        @validates("number")
        def validate_number_iterations(self, value):
            if not (value >= 4):
                raise ValidationError("'number' must be an integer equal or greater than 4.")

class GenerationModelSchema(Schema):
        model = fields.Nested(ModelSchema)

class IterationsSchema(Schema):
        number = fields.Integer(required=True, strict=True)
        @validates("number")
        def validate_number_iterations(self, value):
            if not (0 <= value):
                raise ValidationError("'number' must be an integer equal or greater than 0.")

class ConfigSchema3(Schema):
        test = fields.Nested(ThirdFormatTestCaseSchema, required=True)
        prompts = fields.Nested(PromptSchema, required=True)
        generation = fields.Nested(GenerationModelSchema, required=True)
        iterations = fields.Nested(IterationsSchema, required=True)
class ConfigSchema2(Schema):
        test = fields.Nested(SecondFormatTestCaseSchema, required=True)
        prompts = fields.Nested(PromptSchema, required=True)
        generation = fields.Nested(GenerationModelSchema, required=True)
        iterations = fields.Nested(IterationsSchema, required=True)
class ConfigSchema1(Schema):
        test = fields.Nested(FirstFormatTestCaseSchema, required=True)
        prompts = fields.Nested(PromptSchema, required=True)
        generation = fields.Nested(GenerationModelSchema, required=True)
        iterations = fields.Nested(IterationsSchema, required=True)