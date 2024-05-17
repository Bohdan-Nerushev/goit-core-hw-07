from collections import UserDict
from datetime import datetime, timedelta
import re

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Invalid phone number format: must be exactly 10 digits")

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, value):
        try:
            pattern = r'\b\d{2}\.\d{2}\.\d{4}\b'
            match = re.search(pattern, value)
            if match:
                date_value = datetime.strptime(value, '%d.%m.%Y').date()
                super().__init__(date_value)
            else:
                raise ValueError("Invalid date format. Use DD.MM.YYYY")
        except ValueError as e:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from e

    def __str__(self):
        return self.value.strftime('%d.%m.%Y')

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        phone = self.find_phone(old_phone)
        if phone:
            phone.value = new_phone
        else:
            raise ValueError("Phone not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def info_birthday(self):
        return self.birthday

    def __str__(self):
        phones = "; ".join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        if not isinstance(record, Record):
            raise ValueError("Only Record objects can be added to the AddressBook.")
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.now().date()
        for record in self.data.values():
            if isinstance(record, Record) and record.birthday:
                birthday_date = record.birthday.value
                birthday_this_year = birthday_date.replace(year=today.year)
                if today <= birthday_this_year <= today + timedelta(days=days):
                    upcoming_birthdays.append(
                        {"name": record.name.value, "birthday": birthday_this_year.strftime("%d.%m.%Y")}
                    )
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError, TypeError) as e:
            return str(e)
    return inner

def parse_input(user_input):
    return user_input.lower().strip().split()

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Please provide both a name and a phone number."
    name, phone = args[:2]
    try:
        phone = Phone(phone)  # Validate phone number
    except ValueError as e:
        return str(e)

    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    record.add_phone(phone.value)
    return message

@input_error
def change_contact(book: AddressBook, name, new_phone):
    try:
        new_phone = Phone(new_phone).value  # Validate phone number
    except ValueError as e:
        return str(e)

    record = book.find(name)
    if record:
        if len(record.phones) == 0:
            return "No phone numbers to change."
        old_phone = record.phones[0].value
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return "Contact not found."

@input_error
def show_phone(book: AddressBook, name):
    record = book.find(name)
    if record:
        return ", ".join(str(phone) for phone in record.phones)
    else:
        return "Contact not found."

@input_error
def show_all(book: AddressBook):
    contacts_info = [str(record) for record in book.data.values() if isinstance(record, Record)]
    return '\n'.join(contacts_info) or "Contact list is empty."

@input_error
def add_birthday(book: AddressBook, name, birthday):
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added/updated."
    else:
        return "Contact not found."

@input_error
def show_birthday(book: AddressBook, name):
    record = book.find(name)
    if record and record.birthday:
        return f"{record.name.value}'s birthday: {record.info_birthday()}"
    else:
        return "Birthday information not found."

@input_error
def birthdays(book: AddressBook, days=7):
    upcoming_birthdays = book.get_upcoming_birthdays(days)
    if upcoming_birthdays:
        result = "Upcoming birthdays:\n"
        result += "\n".join(f"{info['name']}: {info['birthday']}" for info in upcoming_birthdays)
        return result
    else:
        return "No upcoming birthdays."

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            print("Please enter a command.")
            continue
        
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            if len(args) < 2:
                print("Please provide a contact name and the new phone number.")
            else:
                print(change_contact(book, args[0], args[1]))
        elif command == "phone":
            if args:
                print(show_phone(book, args[0]))
            else:
                print("Please provide a contact name for the phone command.")
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            if len(args) < 2:
                print("Please provide both a contact name and a birthday.")
            else:
                print(add_birthday(book, args[0], args[1]))
        elif command == "show-birthday":
            if args:
                print(show_birthday(book, args[0]))
            else:
                print("Please provide a contact name for the show-birthday command.")
        elif command == "birthdays":
            days = int(args[0]) if args else 7
            print(birthdays(book, days))
        else:
            print("Invalid command. Please try again.")

if __name__ == '__main__':
    main()

