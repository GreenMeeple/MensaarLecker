# 🍽 🥨 MensaarLecker -- A beloved tool to find out Mensa Ladies' favourite menu 🥨 🍽

As an [UdS](https://www.uni-saarland.de/start.html) Student, 
Are you tired of seeing french fries🍟 3 times a week, or wondering when I can have the best pizza 🍕 in the Mensacafe?
MensaarLecker aims to collect all the data from Menu 1, 2, and Mensacafe to trace your favourite, or Mensa Ladies', favourite menu!

---

## 🥗 Description

A fully automated scraper and menu site for the Saarbrücken Mensa, powered by Python, Selenium, Google Sheets, and GitHub Actions.

> Get a daily-updated overview of meals from https://mensaar.de, formatted and presented cleanly in your browser.

---

## 📅 Features

- ✅ Scrapes the Mensa SB daily menu
- ✅ Publishes data to a connected Google Sheet
- ✅ Generates beautiful, static HTML pages:
  - **Main page** showing today's meals
  - **Full menu** with search, filter & component frequencies
- ✅ GitHub Actions auto-refresh daily at **10:00 AM (CET/CEST weekdays)**
- ✅ Fully open-source & self-hostable

---

## 🌐 Live Demo

> 🖥 [Visit the Menu Website](https://your-github-username.github.io/MensaarLecker)

_Replace with your GitHub Pages link after setup._

---

## 📁 Project Structure

```bash
.
├── generate_menu.py         # Generates index.html and menu.html from Google Sheet
├── Mensaar_scraper.py       # Scrapes data and writes to Google Sheet
├── credentials.json         # Google service account key (not committed)
├── index.html               # Main website page (today's menu)
├── menu.html                # Full searchable menu page
├── .github/workflows/
│   └── update_menu.yml      # GitHub Action to auto-update daily
└── README.md

