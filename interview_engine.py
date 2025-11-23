# interview_engine.py

class InterviewEngine:
    def __init__(self):
        self.roles = [
            "Software Developer",
            "Data Scientist",
            "Frontend Engineer",
            "Backend Engineer",
            "Full Stack Engineer",
            "Machine Learning Engineer",
            "Sales Associate",
            "Technical Support Engineer",
            "QA Engineer"
        ]
        self.history = []

    def available_roles(self):
        """Return list of roles to the Streamlit app."""
        return self.roles

    def ask_question(self, role):
        """Return a mock interview question based on the role."""
        questions = {
            "Software Developer": "Tell me about a challenging bug you fixed recently.",
            "Data Scientist": "Explain the difference between supervised and unsupervised learning.",
            "Frontend Engineer": "How do you optimize performance in a React application?",
            "Backend Engineer": "Explain how you design a scalable API.",
            "Full Stack Engineer": "How do you manage state across a full-stack application?",
            "Machine Learning Engineer": "Describe how you would handle model drift.",
            "Sales Associate": "How do you handle objections from customers?",
            "Technical Support Engineer": "Tell me how you diagnose an unknown technical problem.",
            "QA Engineer": "How do you create an effective test plan?"
        }
        return questions.get(role, "Why should we hire you?")

    def evaluate_answer(self, answer):
        """Provide simple feedback — can be expanded later."""
        if len(answer.split()) < 5:
            return "Your answer is too short. Try giving more details."
        if "team" in answer.lower():
            return "Good — mentioning teamwork is a strong point."
        if "experience" in answer.lower():
            return "Nice — highlighting past experience helps."

        return "Good answer. Try to include examples to make it stronger."
