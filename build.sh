cd core
docker build -t doggy_cam_core .
cd ..

cd server
docker build -t doggy_cam_server .
cd ..

cd relay
docker build -t doggy_cam_relay .
cd ..

docker tag doggy_cam_relay:latest jackmead515/doggy_cam_relay:$1
docker tag doggy_cam_server:latest jackmead515/doggy_cam_server:$1
docker tag doggy_cam_core:latest jackmead515/doggy_cam_core:$1

docker push jackmead515/doggy_cam_relay:$1
docker push jackmead515/doggy_cam_server:$1
docker push jackmead515/doggy_cam_core:$1