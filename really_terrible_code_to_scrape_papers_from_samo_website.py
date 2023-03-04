import aiohttp, asyncio, os

whitelisted_pdfs = ['https://www.samf.ac.za/content/files/QuestionPapers/j2q2015.pdf',
                    'https://www.samf.ac.za/content/files/QuestionPapers/j2s2015.pdf',
                    'https://www.samf.ac.za/content/files/QuestionPapers/s2s2020.pdf',
                    'https://www.samf.ac.za/content/files/QuestionPapers/j3s2020.pdf', # missing due to COVID
                    'https://www.samf.ac.za/content/files/QuestionPapers/j3q2020.pdf'] # missing due to COVID

missing_pdfs = ['https://www.samf.ac.za/content/files/QuestionPapers/s3s1997.pdf', # papers that don't exist on their website, but are purported to exist
                'https://www.samf.ac.za/content/files/QuestionPapers/j2q2004.pdf',
                'https://www.samf.ac.za/content/files/QuestionPapers/s3s2004.pdf']

async def curl_pdfs(questions_solutions=None, round=None, year=None, junior_senior=None, grade='', manual_request=None):

    url = manual_request or f"https://www.samf.ac.za/content/files/QuestionPapers/{junior_senior}{round}{questions_solutions}{grade}{year}.pdf"

    if url in whitelisted_pdfs or url in missing_pdfs:
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content = await resp.read()

    # check whether the file actually exists by checking whether html is sent back instead of a pdf
    if content.startswith(b'<!DOCTYPE html'):
        print(url)

    junior_senior = "Junior" if junior_senior == "j" else "Senior"
    questions_solutions = "Questions" if questions_solutions == "q" else "Solutions"

    if not os.path.exists(dir_path := f"{junior_senior} {questions_solutions} Round {round}"):
        os.makedirs(dir_path)


    grade = f" Grade {grade}" if grade != '' else ''
    with open(f"{dir_path}/{junior_senior} Paper Round {round} {questions_solutions} {grade}{year}.pdf", "wb") as pdf:
        pdf.write(content)

tasks = []
# senior papers and memos
async def do_loop():
    for questions_solutions in ["q", "s"]:
        for round in range(1, 4):
            for year in range(1997, 2023):
                tasks.append(curl_pdfs(questions_solutions, round, year, 's'))
            for year in range(2004, 2011): # junior papers start at 2004
                tasks.append(curl_pdfs(questions_solutions, round, year, 'j'))
        for round in range(2, 4):
            for year in range(2011, 2023):
                tasks.append(curl_pdfs(questions_solutions, round, year, 'j'))
        for round in range(1, 3):
            for year in range(1998, 2004):
                tasks.append(curl_pdfs(questions_solutions, round, year, 'j'))
        for round in range(1, 2):
            for year in range(2011, 2023):
                for grade in [8, 9]:
                    tasks.append(curl_pdfs(questions_solutions, round, year, 'j', grade))
    tasks.append(curl_pdfs('q', 2, 2015, 'j', manual_request="https://www.samf.ac.za/content/files/QuestionPapers/j2q2015b.pdf")) # special files
    tasks.append(curl_pdfs('s', 2, 2015, 'j', manual_request="https://www.samf.ac.za/content/files/QuestionPapers/j2s2015b.pdf"))
    tasks.append(curl_pdfs('s', 2, 2020, 's', manual_request="https://www.samf.ac.za/content/files/QuestionPapers/s2s2020b.pdf"))

    await asyncio.gather(*tasks)

asyncio.run(do_loop())