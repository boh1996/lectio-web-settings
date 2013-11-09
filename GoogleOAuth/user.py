# The Google User class
class GoogleUser:
    def set(self, id, profileUrl, firstName, lastName, gender, picture, email, locale):
        self.id = id
        self.profileUrl = profileUrl
        self.firstName = firstName
        self.lastName = lastName
        self.gender = gender
        self.picture = picture
        self.email = email
        self.fullName = firstName + " " + lastName
        self.locale = locale