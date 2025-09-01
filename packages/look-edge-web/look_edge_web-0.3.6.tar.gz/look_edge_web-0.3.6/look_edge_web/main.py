from .linkedin_browser import open_website

def lookfor_linkedin():
    open_website()

def lookfor_zhipin():
    open_website("zhipin.com", ["直聘","Boss"])

def lookfor_website(target_url: str, title_keywords: list):
    open_website(target_url, title_keywords)

if __name__ == "__main__":
    lookfor_linkedin()
    lookfor_zhipin()