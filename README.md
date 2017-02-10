# Tracktime

Web application which I develop for a small athletic club, which I'm also member of. The intention of this project is to provide a simple solution for management of athletes during a small events. Some of the goals:
- User-friendly interface
- flexible Athlete i.e. participant management
- flexible Group/Category management
- flexible starting list management
- Integration of existing time measurement HW, which the club owns.
- Result management
- Ability to provide the participant, category and start list in a printable form

By 'flexible' I mean, that is shouldn't be problem to add participant on the fly (e.g. shortly before the event starts)

### Time measurement HW
The application should be able to obtain measured times. Times of the athletes are measured by the following hardware:
- ALGE TIMY 3 handheld timer
- other ALGE TIMY impulse devices

ALGE TIMY 3 provides a USB interface and using PyUSB Python module, it is possible to obtain the times.


### Application back-end
This is a web application based on Flask micro-web framework. Besides that, at the moment I'm also utilizing:
- Flask-WTF
- SQLAlchemy
- XLRD
- PyUSB

#### Disclaimer
I'm not experienced nor professional developer. You will notice that in my code.


I decided to share my code. Feel free to use it.
Hope you find this helpful.
Frank
