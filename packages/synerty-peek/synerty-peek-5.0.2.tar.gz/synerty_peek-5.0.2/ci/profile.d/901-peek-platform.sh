# This file is sourced
# Peek platform environment

export PATH="SED_PEEK_VENV_DIR/bin:$PATH"
export PATH="SED_PEEK_SCRIPTS_DIR:$PATH"
export PATH="SED_PEEK_NODEJS_DIR/bin:$PATH"

export SQLITE_TMPDIR="SED_PEEK_TMP_HOME"

alias p_cd_admin='cd SED_PEEK_SRC_SYMLINK/peek_admin_app'
alias p_cd_field='cd SED_PEEK_SRC_SYMLINK/peek_field_app'
alias p_cd_office='cd SED_PEEK_SRC_SYMLINK/peek_office_app'
alias p_cd_ednar='cd SED_PEEK_SRC_SYMLINK/peek_plugin_zepben_ednar_dms_diagram/_private/office-app'

alias p_cd_log_logic='cd SED_PEEK_SERVICE_LOG_DIR/peek-logic'
alias p_cd_log_office='cd SED_PEEK_SERVICE_LOG_DIR/peek-office'
alias p_cd_log_field='cd SED_PEEK_SERVICE_LOG_DIR/peek-field'
alias p_cd_log_worker='cd SED_PEEK_SERVICE_LOG_DIR/peek-worker'
alias p_cd_log_agent='cd SED_PEEK_SERVICE_LOG_DIR/peek-agent'

alias p_vi_code="(cd SED_PEEK_SRC_SYMLINK && nvim)"

alias p_vi_cfg_logic="vim SED_PEEK_SERVICE_CONFIG_HOME/peek-logic/config.json"
alias p_vi_cfg_office="vim SED_PEEK_SERVICE_CONFIG_HOME/peek-office/config.json"
alias p_vi_cfg_field="vim SED_PEEK_SERVICE_CONFIG_HOME/peek-field/config.json"
alias p_vi_cfg_worker="vim SED_PEEK_SERVICE_CONFIG_HOME/peek-worker/config.json"
alias p_vi_cfg_agent="vim SED_PEEK_SERVICE_CONFIG_HOME/peek-agent/config.json"
alias p_vi_cfg="vim SED_PEEK_SERVICE_CONFIG_HOME/peek-*/config.json"

alias p_log_tail_logic="tail -F -n200 SED_PEEK_SERVICE_LOG_DIR/peek-logic/peek-logic.log"
alias p_log_tail_office="tail -F -n200 SED_PEEK_SERVICE_LOG_DIR/peek-office/peek-office.log"
alias p_log_tail_field="tail -F -n200 SED_PEEK_SERVICE_LOG_DIR/peek-field/peek-field.log"
alias p_log_tail_worker="tail -F -n200 SED_PEEK_SERVICE_LOG_DIR/peek-worker/peek-worker.log"
alias p_log_tail_agent="tail -F -n200 SED_PEEK_SERVICE_LOG_DIR/peek-agent/peek-agent.log"
alias p_log_tail="peek_watch_all.sh"

alias p_log_less_logic="less SED_PEEK_SERVICE_LOG_DIR/peek-logic/peek-logic.log"
alias p_log_less_office="less SED_PEEK_SERVICE_LOG_DIR/peek-office/peek-office.log"
alias p_log_less_field="less SED_PEEK_SERVICE_LOG_DIR/peek-field/peek-field.log"
alias p_log_less_worker="less SED_PEEK_SERVICE_LOG_DIR/peek-worker/peek-worker.log"
alias p_log_less_agent="less SED_PEEK_SERVICE_LOG_DIR/peek-agent/peek-agent.log"

alias p_log_cat_exceptions="peek_cat_exceptions.sh"

alias p_watch_queues="watch -d -n10 peek_cat_queues.sh"
alias p_watch="peek_watch_all.sh"
alias p_watch_tmux="peek_tmux_logs.sh"

alias p_journal_tail_logic="sudo journalctl -u peek_logic -f"
alias p_journal_tail_office="sudo journalctl -u peek_office -f"
alias p_journal_tail_field="sudo journalctl -u peek_field -f"
alias p_journal_tail_worker="sudo journalctl -u peek_worker -f"
alias p_journal_tail_agent="sudo journalctl -u peek_agent -f"
alias p_journal_tail_all="sudo journalctl -u peek_logic -u peek_office -u peek_field -u peek_worker -u peek_agent -f"

alias p_journal_last20_logic="sudo journalctl -u peek_logic --lines=20 --no-pager"
alias p_journal_last20_office="sudo journalctl -u peek_office --lines=20 --no-pager"
alias p_journal_last20_field="sudo journalctl -u peek_field --lines=20 --no-pager"
alias p_journal_last20_worker="sudo journalctl -u peek_worker --lines=20 --no-pager"
alias p_journal_last20_agent="sudo journalctl -u peek_agent --lines=20 --no-pager"
alias p_journal_last20_all="sudo journalctl -u peek_logic -u peek_office -u peek_field -u peek_worker -u peek_agent --lines=20 --no-pager"

alias p_sys_restart_logic="
    sudo systemctl restart peek_logic;
    clear;
    p_journal_last20_logic;
    tail -F -n0 SED_PEEK_SERVICE_LOG_DIR/peek-logic/peek-logic.log
"
alias p_sys_restart_worker="
    sudo systemctl restart peek_worker;
    clear;
    p_journal_last20_worker;
    tail -F -n0 SED_PEEK_SERVICE_LOG_DIR/peek-worker/peek-worker.log
"
alias p_sys_restart_field="
    sudo systemctl restart peek_field;
    clear;
    p_journal_last20_field;
    tail -F -n0 SED_PEEK_SERVICE_LOG_DIR/peek-field/peek-field.log
"
alias p_sys_restart_office="
    sudo systemctl restart peek_office;
    clear;
    p_journal_last20_office;
    tail -F -n0 SED_PEEK_SERVICE_LOG_DIR/peek-office/peek-office.log
"
alias p_sys_restart_agent="
    pkill -f run_peek_agent_service;
    sudo systemctl restart peek_agent;
    clear;
    p_journal_last20_agent;
    tail -F -n0 SED_PEEK_SERVICE_LOG_DIR/peek-agent/peek-agent.log
"
alias p_sys_restart="
    peek_restart_all.sh;
    p_journal_last20_all;
    peek_watch_all.sh
"

alias p_sys_stop_logic="sudo systemctl stop peek_logic"
alias p_sys_stop_worker="sudo systemctl stop peek_worker"
alias p_sys_stop_field="sudo systemctl stop peek_field"
alias p_sys_stop_office="sudo systemctl stop peek_office"
alias p_sys_stop_agent="
    pkill -f run_peek_agent_service;
    sudo systemctl stop peek_agent
"
alias p_sys_stop="peek_stop_all.sh"

alias p_sys_enable_logic="sudo systemctl enable peek_logic"
alias p_sys_enable_worker="sudo systemctl enable peek_worker"
alias p_sys_enable_field="sudo systemctl enable peek_field"
alias p_sys_enable_office="sudo systemctl enable peek_office"
alias p_sys_enable_agent="sudo systemctl enable peek_agent"

alias p_sys_disable_logic="sudo systemctl disable peek_logic"
alias p_sys_disable_worker="sudo systemctl disable peek_worker"
alias p_sys_disable_field="sudo systemctl disable peek_field"
alias p_sys_disable_office="sudo systemctl disable peek_office"
alias p_sys_disable_agent="sudo systemctl disable peek_agent"

