def flesch_mapping(score: int):
    if score >= 90:
        return "5. klasa podstawówki"
    if score >= 80:
        return "6. klasa podstawówki"
    if score >= 70:
        return "7. klasa podstawówki"
    if score >= 60:
        return "7. i 8. klasa podstawówki"
    if score >= 50:
        return "Licealista"
    if score >= 30:
        return "Student"
    if score >= 10:
        return "Absolwent szkoły wyższej"
    else:
        return "Profesjonalista"

def fog_mapping(score: int):
    if score >= 17:
        return "Absolwent szkoły wyższej"
    if score >= 16:
        return "Student 4. roku"
    if score >= 15:
        return "Student 3. roku"
    if score >= 14:
        return "Student 2. roku"
    if score >= 13:
        return "Student 1. roku"
    if score >= 12:
        return "Licealista 4. klasy"
    if score >= 11:
        return "Licealista 3. klasy"
    if score >= 10:
        return "Licealista 2. klasy"
    if score >= 9:
        return "Licealista 1. klasy"
    if score >= 8:
        return "8. klasa podstawówki"
    if score >= 7:
        return "7. klasa podstawówki"
    else:
        return "6. klasa podstawówki"

def smog_mapping(score: int):
    if score >= 18:
        return "Student"
    if score >= 17:
        return "Licealista 4. klasy"
    if score >= 16:
        return "Licealista 3. klasy"
    if score >= 15:
        return "Licealista 2. klasy"
    if score >= 14:
        return "Licealista 1. klasy"
    if score >= 13:
        return "8. klasa podstawówki"
    if score >= 12:
        return "7. klasa podstawówki"
    if score >= 11:
        return "6. klasa podstawówki"
    if score >= 10:
        return "5. klasa podstawówki"
    if score >= 9:
        return "4. klasa podstawówki"
    if score >= 8:
        return "3. klasa podstawówki"
    if score >= 7:
        return "2. klasa podstawówki"
    if score >= 6:
        return "1. klasa podstawówki"
    else:
        return "Przedszkole"
