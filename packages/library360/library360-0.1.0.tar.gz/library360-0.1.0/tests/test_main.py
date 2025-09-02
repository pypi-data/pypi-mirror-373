import library360 from Library
amirkabir = Library()
print(amirkabir.add_book("shimi" , "tarverdi"))
print("-" * 20)

print(amirkabir.add_book("riazi" , "mosa khani"))
print("-" * 20)

print(amirkabir.add_book("pyzic" , "Tahreian"))
print("-" * 20)

print(amirkabir.show_book())
print("-" * 20)

print(amirkabir.remove_book("riazi"))
print("-" * 20)

print(amirkabir.show_book())
print("-" * 20)
print(amirkabir.search_book("shimi"))
