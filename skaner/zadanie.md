# Zadanie - Skaner dla wyrażeń matematycznych

- Skanujemy wyrażenie matematyczne, np. 2+3*(76+8/3)+ 3*(9-3)
- Określ zbiór tokenów do skanowania (nazwa/kod i opis) i język implementacji
- Napisz program rozpoznający i wypisujący tokeny - pary: (kod, wartość) 
    - funkcja skaner wywoływana w pętli do napotkania końca wyrażenia
    - rozpoznawane tokeny: liczba całkowita, identyfikator, działania '+,-,*,/', nawiasy '(,)'
- Uzupełnij powyższy program o:
    - obsługę błędów skanera, w tym odpowiednie komentarze
    - lokalizację błędu, tu: numer kolumny gdzie rozpoczyna się błędny token
    - pomijanie spacji i innych białych znaków pomiędzy tokenami, jako pierwszy etap skanowania