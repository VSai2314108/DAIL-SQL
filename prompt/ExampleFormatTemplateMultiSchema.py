import json


class SqlExampleStyle(object):
    """Only show sqls as examples
    
    """
    def get_example_prefix(self):
        return "/* Some SQL examples along with there foreign keys and conditions are provided based on similar problems: */\n"

    def format_example(self, example: dict):
        return +"Foreign Keys: " + example["fk"] + "\n Conditions: " + example["cond"] + "\n" + example['query']
    
    
class QuestionSqlExampleStyle(object):
    """Provide QA pair as examples
    
    """
    def get_example_prefix(self):
        return "/* Some SQL examples are provided based on similar problems: */\n"
    
    def format_schema_link(self, example: dict):
        template_qa = "/* Find the Conditions and Foreign Keys Needed: {}*/\n{}\n{}"
        fk = "Foreign Keys: " + example["fk"]
        cond = "Conditions: " + example["cond"]
        return template_qa.format(example['question'], fk, cond)
    
    def format_example(self, example: dict):
        template_qa = "/* Answer the following: {}*/\n{}\n{}\n{}"
        fk = "Foreign Keys: " + example["fk"]
        cond = "Conditions: " + example["cond"]
        return template_qa.format(example['question'], fk, cond, example['query'])


class QuestionSqlWithRuleExampleStyle(object):
    """Provide QA pair as examples

    """

    def get_example_prefix(self):
        return "/* Some SQL examples are provided based on similar problems: */\n"

    def format_example(self, example: dict):
        template_qa = "/* Answer the following with no explanation: {} */\n{}"
        return template_qa.format(example['question'], example['query'])
    
    
class CompleteExampleStyle(object):
    """Examples are in the same format as target question
    
    """
    def get_example_prefix(self):
        return ""
    
    def format_example(self, example: dict):
        return f"{self.format_question(example)}\n{example['query']}"


class NumberSignQuestionSqlExampleStyle(object):
    """
    Provide QA pair as examples
    """

    def get_example_prefix(self):
        return "### Some example pairs of question and corresponding SQL query are provided based on similar problems:\n\n"

    def format_example(self, example: dict):
        template_qa = "### {}\n{}"
        return template_qa.format(example['question'], example['query'])


class BaselineQuestionSqlExampleStyle(object):
    """
    Provide QA pair as examples
    """

    def get_example_prefix(self):
        return ""

    def format_example(self, example: dict):
        template_qa = "Example Q: {}\nExample A: {}"
        return template_qa.format(example['question'], example['query'])
