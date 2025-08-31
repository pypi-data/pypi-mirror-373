# 创建虚拟主机
rabbitmqctl add_vhost sz_market
rabbitmqctl add_vhost sh_market

# 创建用户
rabbitmqctl add_user sz_user sz_pass
rabbitmqctl add_user sh_user sh_pass

# 设置用户权限 (configure, write, read)
rabbitmqctl set_permissions -p sz_market sz_user ".*" ".*" ".*"
rabbitmqctl set_permissions -p sh_market sh_user ".*" ".*" ".*"
