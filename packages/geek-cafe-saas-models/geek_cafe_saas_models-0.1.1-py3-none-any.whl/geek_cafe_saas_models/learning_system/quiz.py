"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

class Quiz:
    """
    Quiz Model.  Defines a single quiz.
    """
    def __init__(self, name, questions):
        """
        Constructor for a Quiz object.
        :param name: The name of the quiz.
        :param questions: A list of Question objects.
        """
        self.name = name
        self.questions = questions

    def __str__(self):
        """
        String representation of a Quiz object.
        :return: A string containing the quiz name and the number of questions.
        """
        return f"Quiz: {self.name} ({len(self.questions)} questions)"
    