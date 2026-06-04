from models.section import Section

class Layout:
    # sections: list of all the section names NOTE sections have inherent order
    # dict of articles by ID? or list of tuples??
    # articles

    # membership: 
    # unassigned
    # TODO articles should have order also

    # methods:
    # - move an article to a new section
    # - add a section
    # - change section orders

    sections = []

    def move_article(article_id, destination_section):
        ...

    def reorder_sections():
        ...
    
    def add_section(section_name: str):
        ...

    def delete_section():
        """
        Move all articles in section to unassigned, then
        remove section from the Layout
        """
        ...

    

# for article in section:
# - display container
# - display "move to" or "add to" depending on status
# - display drop down where defeault selection is current container

# not in report, query results