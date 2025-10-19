# 🎮 Simple Pong Game with Fuzzy Logic AI

This project implements a simple **Pong game** where the **AI paddle** is controlled by a **fuzzy logic system** using `scikit-fuzzy`.

It’s a small but complete demonstration of applying fuzzy logic to a real-time simulation, combining **AI concepts** with **Python programming and visualization**.

---

## 🧠 Technologies Used
- Python 3.10+
- [pygame](https://www.pygame.org/)
- [scikit-fuzzy](https://pythonhosted.org/scikit-fuzzy/)
- NumPy

---

## 🚀 Features
- Real-time fuzzy control of AI paddle  
- Player-controlled bottom paddle  
- Dynamic speed increase after every bounce  
- Visual background and smooth animation  
- Adjustable fuzzy rules and membership functions  

---

## 🧩 Fuzzy Logic Concept

The AI reacts to two inputs:
- `x_diff` — horizontal difference between the ball and the AI paddle  
- `y_diff` — vertical distance between the ball and paddle  

and outputs:
- `paddle_velocity` — how fast (and in which direction) the AI paddle should move.
