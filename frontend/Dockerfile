# 1. Build the react application using node.js
# Source: https://docs.docker.com/engine/reference/builder/#from
FROM node:19-alpine AS build 

WORKDIR /app

COPY . .

RUN npm install && npm run build


# 2. Production stage: Expose build folder using nginx on port 3000 
# The size of the container used for the frontend is much smaller than running/exposing a development server using npm start in the node container.
# Source: https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-docker/
FROM nginx:1.23.4-alpine

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 3000

# use daemon off to run nginx in the foreground (will be displayed in the console of the container)
CMD ["nginx", "-g", "daemon off;"] 
