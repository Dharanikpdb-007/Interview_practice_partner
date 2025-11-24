import random

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
        
        # Expanded question sets
        self.questions = {
            "Software Developer": [
                "Tell me about a challenging bug you fixed recently.",
                "Explain the difference between a process and a thread.",
                "How do you ensure code quality in large projects?",
                "Describe the SOLID principles.",
                "How do you handle version control conflicts?"
            ],
            "Data Scientist": [
                "Explain the difference between supervised and unsupervised learning.",
                "How do you deal with missing data?",
                "What is overfitting and how do you prevent it?",
                "Explain precision, recall, and F1 score.",
                "Describe a real-world machine learning project you worked on."
            ],
            "Frontend Engineer": [
                "How do you optimize performance in a React application?",
                "What are the differences between state and props?",
                "How do you handle cross-browser compatibility issues?",
                "Explain the virtual DOM.",
                "How do you manage global state?"
            ],
            "Backend Engineer": [
                "Explain how you design a scalable API.",
                "How do you ensure database performance at scale?",
                "What is the difference between monolithic and microservices architecture?",
                "Explain authentication vs authorization.",
                "How do you handle rate limiting?"
            ],
            "Full Stack Engineer": [
                "How do you manage state across a full-stack application?",
                "Describe a challenging end-to-end project you built.",
                "How do you secure a full-stack application?",
                "Explain CI/CD in your workflow.",
                "How do frontend and backend communicate efficiently?"
            ],
            "Machine Learning Engineer": [
                "Describe how you would handle model drift.",
                "Explain the ML pipeline lifecycle.",
                "What is feature engineering and why is it important?",
                "How do you deploy large ML models in production?",
                "Explain hyperparameter tuning techniques."
            ],
            "Sales Associate": [
                "How do you handle objections from customers?",
                "Describe a successful sales pitch you delivered.",
                "How do you build rapport with clients?",
                "How do you handle a dissatisfied customer?",
                "What motivates you in sales?"
            ],
            "Technical Support Engineer": [
                "Tell me how you diagnose an unknown technical problem.",
                "How do you handle an angry customer?",
                "Describe a time you solved a complex issue quickly.",
                "How do you document troubleshooting steps?",
                "Explain your approach to root-cause analysis."
            ],
            "QA Engineer": [
                "How do you create an effective test plan?",
                "What is the difference between verification and validation?",
                "Explain the SDLC and STLC.",
                "Describe automation vs manual testing.",
                "How do you prioritize test cases?"
            ]
        }

        self.history = []

    def available_roles(self):
        """Return list of roles."""
        return self.roles

    def ask_question(self, role):
        """Return a random question based on the role."""
        return random.choice(self.questions.get(role, ["Why should we hire you?"]))

    def evaluate_answer(self, answer):
        """Provide simple feedback — can be expanded later."""
        if len(answer.split()) < 5:
            return "Your answer is too short. Try giving more details."
        if "team" in answer.lower():
            return "Good — mentioning teamwork is a strong point."
        if "experience" in answer.lower():
            return "Nice — highlighting past experience helps."

        return "Good answer. Try to include examples from your past experience."
