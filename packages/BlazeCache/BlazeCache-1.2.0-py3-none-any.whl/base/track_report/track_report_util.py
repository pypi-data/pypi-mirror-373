from base.log import log_util
from datetime import datetime
import time


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class EventTracker:
    '''
    该类为单例模式, 全局只有一个实例对象
    负责计时统计功能, 会记录所有 event 事件的耗时情况
    
    使用示例:
    event_tracker.record_start("event_name")
    ...
    event_tracker.record_end("event_name")
    '''
    def __init__(self):
        self.events = {}
        self.postEvents = {}
        self.logger = log_util.BccacheLogger(name="EventTracker")

    def record_start(self, event_name: str, product_name: str):
        
        now = datetime.now()

        if product_name not in self.events:
            self.events[product_name] = {
                event_name: {
                    'start_time': now
                }
            }
            self.logger.info("[EventTracker] event: {} start. product: {}".format(event_name, product_name))
        elif event_name not in self.events[product_name]:
            self.events[product_name] = {
                event_name: {
                    'start_time': now
                }
            }
            self.logger.info("[EventTracker] event: {} start. product: {}".format(event_name, product_name))
        else:
            self.logger.info('[EventTracker] event: {} already exists. product: {}'.format(event_name, product_name))

    def record_end(self, event_name: str, product_name: str):
        now = datetime.now()
        if product_name not in self.events:
            self.logger.info("[EventTracker] product: {} not created.".format(product_name))
        elif event_name not in self.events[product_name]:
            self.logger.info("[EventTracker] event: {} not created.".format(event_name))
        else:
            self.events[product_name][event_name]['end_time'] = now
            self.logger.info("[EventTracker] event: {} end. product: {}".format(event_name, product_name))

    def get_time_elapsed(self, event_name: str, product_name: str, is_format_time: bool = False):
        '''
        获取单一事件的耗时时间
        
        Args:
            is_format_time: 是否返回格式化后的时间 
        '''
        if product_name in self.events and event_name in self.events[product_name] and len(self.events[product_name][event_name]) > 1:
            end_time = self.events[product_name][event_name]['end_time']
            start_time = self.events[product_name][event_name]['start_time']
            time_delta = end_time - start_time

            seconds = time_delta.total_seconds()
            
            if not is_format_time:
                return seconds
            
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours >= 1:
                return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
            elif minutes >= 1:
                return '{} m {} s'.format(int(minutes), int(seconds))
            else:
                return '{} s'.format(int(seconds))

    def print_table(self):
        '''
        输出全量 events 耗时的接口
        该接口一般用于整个项目运行结束后, 打印所有 events 耗时情况
        
        Returns:
            postEvents: 返回一个 Dict 结构, 记录了所有 event 事件的耗时, 单位为秒
            一般用于数据上报
        '''
        self.logger.info("{:<20} {:<20} {:<20}".format('Event', 'Product', 'Time elapsed'))
        for product_name in self.events:
            event_dict = self.events[product_name]
            for event_name in event_dict:
                time_elapsed = self.get_time_elapsed(event_name, product_name, True)
                get_event_time = self.get_time_elapsed(event_name, product_name)
                self.logger.info("{:<20} {:<20} {:<20}".format(event_name, product_name, time_elapsed))
                if get_event_time:
                    self.postEvents[product_name] = {
                        event_name: get_event_time
                    }
        
        
        self.logger.info(self.postEvents)

        return self.postEvents


   
if __name__ == "__main__":
    tracker = EventTracker()
    tracker.record_start("Test", "Lark")
    time.sleep(10)
    tracker.record_end("Test", "Lark")
    tracker.print_table()