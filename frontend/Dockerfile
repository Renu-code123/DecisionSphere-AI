# Stage 1: Build React App
FROM node:20-alpine AS build

WORKDIR /workspace

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

COPY --from=build /workspace/dist /usr/share/nginx/html

# Copy custom nginx configuration to handle SPA routing if needed
# For now, default Nginx is sufficient for this SPA build.

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
