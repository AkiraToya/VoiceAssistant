# Project Installation
Use conda:
```
conda create -p env python=3.11
conda activate ./env
pip install -r requirements.txt
```

After install all files needed:
```
python main.py
```

# StyleTTS2 Installation
go to modules folder and type:
```
git clone https://github.com/yl4579/StyleTTS2.git
cd StyleTTS2
pip install -r requirements.txt
```

on windows run one more command:
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -U
```

then install:
```
pip install phonemizer
```

on windows install: espeak-ng for windows and set the location at tts.py code:
```
EspeakWrapper.set_library('C:\Program Files\eSpeak NG\libespeak-ng.dll')
```