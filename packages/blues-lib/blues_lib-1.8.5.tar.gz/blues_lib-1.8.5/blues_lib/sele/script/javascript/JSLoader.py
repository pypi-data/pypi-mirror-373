class JSLoader():

  def load_script(self,url):
    '''
    @description : 导入线上/本地 js脚本，用异步执行，保证python等待资源加载完毕
    @param {str} url : the scirpt file's path
    '''
    callback = "var callback = arguments[arguments.length-1];"
    create_script = "var sele_script=document.createElement('script');sele_script.src='%s';" % url
    # 在onload中执行callback，通知python js脚本已结束
    onload_script = "sele_script.onload=function(){callback();console.log('%s loaded by the selenium!')};" % url
    append_script = "var head=document.getElementsByTagName('head')[0];head.appendChild(sele_script);"
    load_script = "%s %s %s %s" % (callback,create_script,onload_script,append_script)
    # wait the script loaded, Determine whether it is complete according to the dynamic insertion mark 'selenium-dynamic-script'
    return self.execute_async(load_script)

  def load_blues(self):
    js_script = BluesJavaScriptService.service_script
    self.execute(js_script)

  def load_plugin(self,plugins):
    '''
    @description : load relay plugin auto
    @param {dict} plugins 
      - key : the global var name
      - value : the plugin's cdn
    '''
    for plugin_var,plugin_cdn in plugins.items():
      print('===>',plugin_var,plugin_cdn)
      if self.is_var_available(plugin_var):
        continue
      self.load_script(plugin_cdn)
