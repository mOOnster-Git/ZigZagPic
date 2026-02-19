# GitHub 업로드 가이드 (초보자용)

이 문서는 **ZigZag Pic** 프로젝트를 GitHub에 처음 올리는 분들을 위해 작성되었습니다.
천천히 하나씩 따라 하시면 됩니다!

---

## 1단계: GitHub 저장소 만들기
1.  [GitHub](https://github.com)에 로그인합니다. (계정이 없다면 가입하세요)
2.  우측 상단의 **+** 아이콘을 누르고 **New repository**를 클릭합니다.
3.  **Repository name**에 `ZigZagPic`이라고 입력합니다.
4.  **Public** (공개) 또는 **Private** (비공개) 중 원하는 것을 선택합니다.
    *   다른 사람들과 공유하려면 **Public**을 선택하세요.
5.  아래의 "Add a README file", ".gitignore", "license" 체크박스는 **모두 체크 해제** 상태로 둡니다. (이미 로컬에 파일이 있으니까요!)
6.  맨 아래 **Create repository** 초록색 버튼을 클릭합니다.
7.  생성된 페이지에 나오는 주소(`https://github.com/사용자명/ZigZagPic.git`)를 복사해둡니다.

---

## 2단계: 내 컴퓨터에서 Git 설정하기 (터미널)
Trae 에디터 하단에 있는 터미널(Terminal) 창을 엽니다.

### 1. Git 사용자 정보 등록 (처음 한 번만 필요)
본인의 GitHub 이메일과 이름을 입력하세요.
```bash
git config --global user.email "moonsoo24@gmail.com"
git config --global user.name "mOOnster-Git"
```

### 2. 프로젝트 초기화
이미 프로젝트 폴더(`ZigZagPic`)에 있다고 가정합니다.
```bash
git init
```
*(Initialized empty Git repository... 메시지가 나오면 성공)*

### 3. 파일 담기 (Staging)
업로드할 파일들을 장바구니에 담는 과정입니다.
```bash
git add .
```
*(점(.)은 현재 폴더의 모든 파일을 의미합니다)*

### 4. 저장하기 (Commit)
담은 파일들에 설명을 붙여서 저장합니다.
```bash
git commit -m "First commit: ZigZag Pic v2.2.4 release"
```

---

## 3단계: GitHub에 올리기 (Push)

### 1. 원격 저장소 연결
아까 1단계에서 복사해둔 주소를 여기에 붙여넣으세요.
```bash
git remote add origin https://github.com/본인아이디/ZigZagPic.git
```
*(만약 `fatal: remote origin already exists.` 오류가 나면 `git remote remove origin` 입력 후 다시 하세요)*

### 2. 업로드 (Push)
```bash
git branch -M main
git push -u origin main
```

---

## 🎉 축하합니다!
이제 GitHub 페이지를 새로고침(F5) 해보세요.
작성하신 코드와 `README.md` 설명이 예쁘게 올라가 있는 것을 볼 수 있습니다.

### 💡 실행 파일(EXE)은 어떻게 하나요?
GitHub 저장소에는 주로 **소스 코드**만 올립니다.
`dist/ZigZagPic_v2.2.4.exe` 파일은 용량이 커서 직접 올리기보다는, GitHub 저장소 우측의 **Releases** 기능을 이용해 별도로 업로드하는 것이 정석입니다.

1.  GitHub 저장소 우측 **Releases** 클릭 -> **Draft a new release** 클릭.
2.  **Choose a tag**에 `v2.2.4` 입력.
3.  **Release title**에 `ZigZag Pic v2.2.4 배포` 입력.
4.  하단에 `ZigZagPic_v2.2.4.exe` 파일을 드래그해서 첨부.
5.  **Publish release** 클릭.

이렇게 하면 사람들이 소스 코드를 다운받지 않고도 실행 파일만 쉽게 받아갈 수 있습니다!
