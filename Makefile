# SPDX-License-Identifier: MIT
# Copyright 2023 hirmiura (https://github.com/hirmiura)
#
# cs-trans_scripts/
# ├── cs_trans_scripts/  スクリプト
# ├── vanilla_content/   バニラデータ
# ├── tmp/ 作業用
# │   └── vanilla_content/
# │       ├── formatted/  整形
# │       │   ├── core/
# │       │   └── loc_jp/
# │       ├── normalized/  正規化
# │       │   ├── core/
# │       │   └── loc_jp/
# │       ├── diff/   差分
# │       └── patch/  パッチ
#
SHELL := /bin/bash

D_VAN := vanilla_content
D_TMP := tmp
D_FMT := formatted
D_NOR := normalized
D_DIF := diff
D_PAT := patch
D_SCR := cs_trans_scripts

D_CO := core
D_JP := loc_jp

# バニラのディレクトリ
D_VAN_C := $(D_VAN)/$(D_CO)
D_VAN_J := $(D_VAN)/$(D_JP)

# バニラの元ファイル群
L_VJ := $(shell find $(D_VAN_J) -type f -name '*.json')
L_VC := $(L_VJ:$(D_VAN_J)%=$(D_VAN_C)%)

# 整形後のファイル群
D_TMP_VAN     := $(D_TMP)/$(D_VAN)
D_TMP_VAN_FMT := $(D_TMP_VAN)/$(D_FMT)
D_TMP_VAN_FMT_CO := $(D_TMP_VAN_FMT)/$(D_CO)
D_TMP_VAN_FMT_JP := $(D_TMP_VAN_FMT)/$(D_JP)
L_FC := $(L_VC:$(D_VAN)/%=$(D_TMP_VAN_FMT)/%)
L_FJ := $(L_VJ:$(D_VAN)/%=$(D_TMP_VAN_FMT)/%)

# 正規化後のファイル群
D_TMP_VAN_NOR := $(D_TMP_VAN)/$(D_NOR)
D_TMP_VAN_NOR_CO := $(D_TMP_VAN_NOR)/$(D_CO)
D_TMP_VAN_NOR_JP := $(D_TMP_VAN_NOR)/$(D_JP)
L_NC := $(L_VC:$(D_VAN)/%=$(D_TMP_VAN_NOR)/%)
L_NJ := $(L_VJ:$(D_VAN)/%=$(D_TMP_VAN_NOR)/%)

# 差分ファイル群
D_TMP_VAN_DIF := $(D_TMP_VAN)/$(D_DIF)
D_TMP_VAN_PAT := $(D_TMP_VAN)/$(D_PAT)
L_DI := $(L_VC:$(D_VAN_C)/%=$(D_TMP_VAN_DIF)/%)
L_PA := $(L_VC:$(D_VAN_C)/%=$(D_TMP_VAN_PAT)/%)


#==============================================================================
# ヘルプ表示
#==============================================================================
define find.functions
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
endef

.PHONY: help
help:
	@echo '以下のコマンドが使用できます'
	@echo ''
	$(call find.functions)


#==============================================================================
# バニラデータのリンク/ディレクトリを確認
#==============================================================================
.PHONY: check
check: ## バニラデータのリンク/ディレクトリを確認します
check:
	@if [[ -d $(D_VAN) || -L $(D_VAN) && `readlink $(D_VAN) ` ]] ; then \
		echo -e "\033[94m'vanilla_content' is OK.\033[0m" ; \
	else \
		echo -e "\a\033[91m'vanilla_content'にバニラのcontentディレクトリのリンクかコピーを置いて下さい\033[0m" ; \
	fi


#==============================================================================
# 初期化
#==============================================================================
.PHONY: init
init: ## 環境を構築します
init:
	poetry run python -m pip install --upgrade pip setuptools
	poetry update


#==============================================================================
# ビルド
#==============================================================================
.PHONY: all
all: ## ビルドします
all: check init format normalize diff one-file-patch


#==============================================================================
# JSONファイルの整形
#==============================================================================
.PHONY: format
format: ## JSONを整形します
format: check $(L_FC) $(L_FJ)

$(L_FC) $(L_FJ):
	$(eval FN := $(@:$(D_TMP_VAN_FMT)/%=$(D_VAN)/%))
	@mkdir -p $(@D)
	@echo -e "\x1b[32mFormatting\x1b[0m $(FN) > $@"
	@poetry run $(D_SCR)/format_json.py $(FN) > $@


#==============================================================================
# JSONデータの正規化
#==============================================================================
.PHONY: normalize
normalize: ## JSONデータを正規化します
normalize: format $(L_NC) $(L_NJ)

$(L_NC) $(L_NJ):
	$(eval FN := $(@:$(D_TMP_VAN_NOR)/%=$(D_TMP_VAN_FMT)/%))
	@mkdir -p $(@D)
	@echo -e "\x1b[32mNormalizing\x1b[0m $(FN) > $@"
	@poetry run $(D_SCR)/normalize_json.py $(FN) > $@


#==============================================================================
# 差分を取る
#==============================================================================
.PHONY: diff
diff: ## 差分を取ります
diff: normalize $(L_DI)

$(L_DI):
	$(eval FNJ := $(@:$(D_TMP_VAN_DIF)/%=$(D_TMP_VAN_NOR_JP)/%))
	$(eval FNC := $(@:$(D_TMP_VAN_DIF)/%=$(D_TMP_VAN_NOR_CO)/%))
	$(eval FNP := $(@:$(D_TMP_VAN_DIF)/%=$(D_TMP_VAN_PAT)/%))
	@if [ -f $(FNJ) ] ; then \
		mkdir -p $(@D) ; \
		echo -e "\x1b[32mJSONdiffing\x1b[0m $(FNJ) $(FNC) > $@" ; \
		poetry run jsondiff --indent 4 $(FNC) $(FNJ) > $@ ; \
		mkdir -p $(dir $(FNP)) ; \
		echo -e "\x1b[32mJQing\x1b[0m $@ > $(FNP)" ; \
		jq '.[] | select(.op == "replace" and (.path | test("(/drawmessages/|(label|comments|description|descriptionunlocked)$$)")))' $@ | jq -s > $(FNP) ; \
	fi

.PHONY: one-file-patch
one-file-patch: ## パッチファイルを1つにまとめます
one-file-patch: diff $(D_TMP_VAN)/$(D_PAT).json

$(D_TMP_VAN)/$(D_PAT).json: $(L_DI)
	@mkdir -p $(@D)
	find $(D_TMP_VAN_PAT) -type f -size +3c -exec jq -s '.[][]' {} + | jq -s > $@

#==============================================================================
# お掃除
#==============================================================================
.PHONY: clean
clean: ## 削除します
clean: clean-tmp clean-cache

.PHONY: clean-tmp
clean-tmp: ## テンポラリファイルを削除します
clean-tmp:
	rm -fr $(D_TMP)

.PHONY: clean-formatted
clean-formatted: ## 整形済みファイルを削除します
clean-formatted:
	rm -fr $(D_TMP_VAN_FMT)

.PHONY: clean-normalized
clean-normalized: ## 整形済みファイルを削除します
clean-normalized:
	rm -fr $(D_TMP_VAN_NOR)

.PHONY: clean-diff
clean-diff: ## 差分ファイルを削除します
clean-diff: clean-patch

.PHONY: clean-patch
clean-patch: ## 差分ファイルを削除します
clean-patch: clean-one-file-patch
	rm -fr $(D_TMP_VAN_DIF)
	rm -fr $(D_TMP_VAN_PAT)

clean-one-file-patch:
	rm -f $(D_TMP_VAN)/$(D_PAT).json

.PHONY: clean-cache
clean-cache: ## キャッシュファイルを削除します
clean-cache:
	rm -rf .pytest_cache .mypy_cache
	# Remove all pycache
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf


#==============================================================================
# デバッグ用のテストルール
#==============================================================================
.PHONY: test
test: ## デバッグ用です(※pytestは走りません)
test: $(D_TMP_VAN_NOR_CO)/elements/abilities.json $(D_TMP_VAN)/patch.json
	@echo "1. 英語ファイルからJSONポインタを抜き出す" 1>&2
	@echo "2. 日本語化ファイルから(1)の該当部分を抜き出す" 1>&2
	@echo "3. 英語ファイルに(2)のパッチをあてる" 1>&2
	$(D_SCR)/pointers_json.py $(D_TMP_VAN_NOR_CO)/elements/abilities.json \
	| $(D_SCR)/patch_filtered_by_pointers.py $(D_TMP_VAN)/patch.json \
	| jsonpatch -u --indent 4 tmp/vanilla_content/normalized/core/elements/abilities.json /dev/stdin
