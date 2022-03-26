from dataclasses import dataclass, field


@dataclass
class State:
    page: int = 0
    selected_times: set = field(default_factory=set)
    full_name: str = None
    companies: set = field(default_factory=set)
    email: str = None
    difficulty_level: str = None
    theme: str = None

    def set_page(self, page):
        self.page = page

    def clear_state(self):
        self.full_name = None
        self.companies = set()
        self.difficulty_level = None
        self.theme = None
        self.email = None
        self.selected_times = set()