

def cardtl_insert_format():
    return '''
    declare @sid int;
set @sid = -1
select @sid = uid from CarDtl where uid = %d
if @sid = -1
    begin
    insert into CarDtl (
  [src_id],[name],[guide_price],[engine],[gear_box]
      ,[energy_type],[max_power],[max_torque],[oil_wear],[max_horsepower]
      ,[uid]
      ,[size],[structure],[max_speed],[office_acc_time],[true_acc_time]
      ,[true_brake_len],[door_num],[seat_num]
      ,[output_volumn],[cylinder_num] ,[valve_num], [ttm], [grade], [manufacturer], [drive_type]
  ) values (
  '%s', '%s', '%s', '%s', '%s',
  '%s', '%s', '%s', '%s', '%s',
  %d,
  '%s', '%s', '%s', '%s', '%s',
  '%s', %d, %d,
    '%s', %d, %d,'%s', '%s', '%s', '%s'
  )
    end
else
    begin
    print 'fuck'
    end
    '''

def car_join_deduplicate():
    return """
    select * from CarBase a left join ( select  row_number() over (partition by src_id order by id) as group_idx  , src_id
    from CarDtl) b on b.group_idx=1 and  a.src_id=b.src_id
    """

class cardtl(object):
    def __init__(self, uid_):
        self._name = ''
        self._uid = uid_
        self._src_id = ''
        self._guide_price = ''
        self._energy_type = ''
        self._ttm = ''
        self._max_power = ''
        self._max_torque = ''
        self._engine = ''
        self._gear_box = ''
        self._size = ''
        self._structure = ''
        self._max_speed = ''
        self._office_acc_time = ''
        self._true_acc_time = ''
        self._true_brake_len = ''
        self._oil_wear = ''
        self._door_num = 0
        self._seat_num = 0
        self._output_volumn = ''
        # self._intake_form = ''
        self._valve_num = 0
        self._cylinder_num = 0
        self._max_horse = ''
        self._drive_type = ''
        self._manufacturer = ''
        self._grade = ''

    def cardtl_insert_tuple(self):
        return self._uid, self._src_id, self._name, self._guide_price, self._engine, self._gear_box,\
            self._energy_type, self._max_power, self._max_torque, self._oil_wear, self._max_horse,\
                self._uid, \
                self._size, self._structure, self._max_speed, self._office_acc_time,self._true_acc_time,\
                    self._true_brake_len, self._door_num, self._seat_num,\
                        self._output_volumn, self._cylinder_num, self._valve_num, self._ttm, self._grade,\
                            self._manufacturer, self._drive_type


    @property
    def drive_type(self):
        return self._drive_type

    @drive_type.setter
    def drive_type(self, value):
        self._drive_type = value

    @property
    def manufacturer(self):
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        self._grade = value
    

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def src_id(self):
        return self._src_id

    @src_id.setter
    def src_id(self, value):
        self._src_id = value

    @property
    def guide_price(self):
        return self._guide_price

    @guide_price.setter
    def guide_price(self, value):
        self._guide_price = value

    @property
    def energy_type(self):
        return self._energy_type

    @energy_type.setter
    def energy_type(self, value):
        self._energy_type = value

    @property
    def ttm(self):
        return self._ttm
    
    @ttm.setter
    def ttm(self, value):
        self._ttm = value

    @property
    def max_power(self):
        return self._max_power

    @max_power.setter
    def max_power(self, value):
        self._max_power = value

    @property
    def max_torque(self):
        return self._max_torque
    
    @max_torque.setter
    def max_torque(self, value):
        self._max_torque = value

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    @property
    def gear_box(self):
        return self._gear_box

    @gear_box.setter
    def gear_box(self, value):
        self._gear_box = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def structure(self):
        return self._structure

    @structure.setter
    def structure(self, value):
        self._structure = value

    @property
    def max_speed(self):
        return self._max_speed

    @max_speed.setter
    def max_speed(self, value):
        self._max_speed = value

    @property
    def office_acc_time(self):
        return self._office_acc_time

    @office_acc_time.setter
    def office_acc_time(self, value):
        self._office_acc_time = value

    @property
    def true_acc_time(self):
        return self._true_acc_time

    @true_acc_time.setter
    def true_acc_time(self, value):
        self._true_acc_time = value

    @property
    def true_brake_len(self):
        return self._true_brake_len

    @true_brake_len.setter
    def true_brake_len(self, value):
        self._true_brake_len = value

    @property
    def oil_wear(self):
        return self._oil_wear

    @oil_wear.setter
    def oil_wear(self, value):
        self._oil_wear = value

    @property
    def door_num(self):
        return self._door_num

    @door_num.setter
    def door_num(self, value):
        self._door_num = value

    @property
    def seat_num(self):
        return self._seat_num

    @seat_num.setter
    def seat_num(self, value):
        self._seat_num = value

    @property
    def output_volumn(self):
        return self._output_volumn

    @output_volumn.setter
    def output_volumn(self, value):
        self._output_volumn = value

    @property
    def max_horse(self):
        return self._max_horse

    @max_horse.setter
    def max_horse(self, value):
        self._max_horse = value

    @property
    def cylinder_num(self):
        return self._cylinder_num

    @cylinder_num.setter
    def cylinder_num(self, value):
        self._cylinder_num = value

    @property
    def valve_num(self):
        return self._valve_num

    @valve_num.setter
    def valve_num(self, value):
        self._valve_num = value