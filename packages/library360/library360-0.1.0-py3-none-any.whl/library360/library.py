class Library():
    def __init__(self):
        self.book = []
        self.author = []

    def add_book(self, title, author):
        self.book.append(title)
        self.author.append(author)
        return f"book added!"

    def remove_book(self, title):
        self.book.remove(title)
        return f"removed book!!"

    def search_book(self, title):
        for b in self.book:
            if b == title:
                return f" i find book! \n book name : {title} \n author : {self.author[self.book.index(title)]} \n count author book: {self.author.count(self.author[self.book.index(title)])} "

    def show_book(self):
        return f"books : {self.book}"


if __name__ == "__main__":
    lib = Library()
    while True:
        action = input("Enter action (add/search/remove/show/exit): ").lower()
        if action == "add":
            title = input("Book title: ")
            author = input("Author: ")
            print(lib.add_book(title, author))
        elif action == "search":
            title = input("Book title: ")
            print(lib.search_book(title))
        elif action == "remove":
            title = input("Book title: ")
            print(lib.remove_book(title))
        elif action == "show":
            print(lib.show_book())
        elif action == "exit":
            break
        else:
            print("Invalid action!")