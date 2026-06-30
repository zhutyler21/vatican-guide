#!/bin/bash
# macOS: 用 nohup detach batch_tts.py（脚本内部已调 os.setsid 脱离会话）
cd /Users/zhutyler21/Downloads/Hermes/wangning/05-代码/20260630-vatican-guide-app
rm -f /tmp/vatican_tts.done
nohup env TOKENIZERS_PARALLELISM=false \
  /Users/zhutyler21/.hermes/tools/CosyVoice/.venv/bin/python -u batch_tts.py \
  > /tmp/vatican_tts.log 2>&1 < /dev/null &
echo "daemon launched pid=$!"
