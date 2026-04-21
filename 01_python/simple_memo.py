#python simple_memo.py

file_name = input("저장할 파일명:")
print("저장할 내용을 입력하세요. 다 입력하면 !q를 입력하세요.")

with open("text/"+file_name, "wt", encoding="utf-8") as fw:

    save_str = input("저장할 문장:")
    while save_str != "!q":
        fw.write(save_str+"\n")
        save_str = input("저장할 문장:")